import os
import fcntl
import hmac
import hashlib
import json
import time
import uuid
import httpx
import sqlite3
import shutil
import threading
import random
import string
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import parse_qsl
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))
ADMIN_IDS = {ADMIN_ID} if ADMIN_ID > 0 else set()
MONOBANK_CARD = "4441 1111 3196 2080"
PUBG_ID_FOR_UC = "51230579110"
REVIEWS_LINK = os.environ.get("REVIEWS_LINK", "https://t.me/armyanfeedback")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
ORDERS_FILE = DATA_DIR / "orders.json"
PRICES_FILE = DATA_DIR / "prices.json"

# ─── SQLite (колесо, промокоды) ───────────────────────────────────────────────
DB_FILE = DATA_DIR / "miniapp.db"
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

WHEEL_COOLDOWN = 24 * 3600  # 24 часа

WHEEL_SEGMENTS = [
    {"label": "Без выигрыша", "discount": 0,  "weight": 40},
    {"label": "Скидка 5%",    "discount": 5,  "weight": 25},
    {"label": "Скидка 10%",   "discount": 10, "weight": 15},
    {"label": "Скидка 15%",   "discount": 15, "weight": 10},
    {"label": "Скидка 20%",   "discount": 20, "weight": 7},
    {"label": "Скидка 25%",   "discount": 25, "weight": 3},
]


def get_db():
    conn = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wheel_spins (
                user_id INTEGER PRIMARY KEY,
                last_spin TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wheel_promos (
                code TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                discount INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()


def backup_db():
    if not DB_FILE.exists():
        return
    ts = datetime.now().strftime("%Y-%m-%d_%H_%M")
    dst = BACKUP_DIR / f"miniapp_{ts}.db"
    # Используем SQLite online-backup API — безопасно при активных записях
    src_conn = sqlite3.connect(str(DB_FILE))
    dst_conn = sqlite3.connect(str(dst))
    try:
        src_conn.backup(dst_conn)
    finally:
        dst_conn.close()
        src_conn.close()
    # Оставляем только последние 24 бэкапа
    backups = sorted(BACKUP_DIR.glob("miniapp_*.db"))
    for old in backups[:-24]:
        try:
            old.unlink()
        except Exception:
            pass


def _backup_loop():
    while True:
        time.sleep(3600)
        try:
            backup_db()
        except Exception as e:
            print(f"[backup] Ошибка: {e}")


# Инициализация при старте
init_db()
backup_db()
threading.Thread(target=_backup_loop, daemon=True, name="db-backup").start()


def _spin_result():
    total = sum(s["weight"] for s in WHEEL_SEGMENTS)
    r = random.randint(1, total)
    cumulative = 0
    for seg in WHEEL_SEGMENTS:
        cumulative += seg["weight"]
        if r <= cumulative:
            return seg
    return WHEEL_SEGMENTS[0]


def _gen_promo_code(discount: int) -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"WHEEL{discount}-{suffix}"


ORDERS_LOCK_FILE = DATA_DIR / "orders.lock"


@contextmanager
def orders_lock():
    with open(ORDERS_LOCK_FILE, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def save_json(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


INIT_DATA_MAX_AGE = 6 * 3600  # 6 часов


def verify_init_data(init_data: str):
    if not init_data or not BOT_TOKEN:
        return None
    try:
        params = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = params.pop("hash", None)
        if not received_hash:
            return None
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(params.items())
        )
        secret_key = hmac.new(
            b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256
        ).digest()
        expected_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected_hash, received_hash):
            return None
        auth_date = int(params.get("auth_date", "0"))
        if auth_date <= 0 or time.time() - auth_date > INIT_DATA_MAX_AGE:
            return None
        user_str = params.get("user", "{}")
        return json.loads(user_str)
    except Exception:
        return None


def is_admin(init_data: str) -> bool:
    user = verify_init_data(init_data)
    if not user:
        return False
    return int(user.get("id", 0)) in ADMIN_IDS


@app.route("/")
def index():
    prices = load_json(PRICES_FILE, {"uah_price": 800, "uc_price": 1320})
    return render_template(
        "miniapp.html",
        monobank_card=MONOBANK_CARD,
        pubg_id_uc=PUBG_ID_FOR_UC,
        uah_price=prices.get("uah_price", 800),
        uc_price=prices.get("uc_price", 1320),
        admin_ids=sorted(ADMIN_IDS),
        reviews_link=REVIEWS_LINK,
    )


@app.after_request
def add_no_cache_headers(response):
    if response.mimetype == "text/html":
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


@app.route("/api/me", methods=["GET"])
def get_me():
    init_data = request.headers.get("X-Init-Data", "")
    user = verify_init_data(init_data)
    if not user:
        return jsonify({"ok": False, "is_admin": False}), 401
    return jsonify({
        "ok": True,
        "is_admin": int(user.get("id", 0)) in ADMIN_IDS,
    })


@app.route("/api/my_orders", methods=["GET"])
def get_my_orders():
    init_data = request.headers.get("X-Init-Data", "")
    user = verify_init_data(init_data)
    if not user:
        return jsonify({"ok": False, "error": "Открой приложение через Telegram"}), 401
    uid = str(user.get("id", ""))
    orders = [o for o in load_json(ORDERS_FILE, []) if o.get("user_id") == uid]
    return jsonify({"ok": True, "orders": list(reversed(orders))})


@app.route("/api/prices", methods=["GET"])
def get_prices():
    prices = load_json(PRICES_FILE, {"uah_price": 800, "uc_price": 1320})
    return jsonify(prices)


@app.route("/api/prices", methods=["POST"])
def update_prices():
    init_data = request.headers.get("X-Init-Data", "")
    if not is_admin(init_data):
        return jsonify({"ok": False, "error": "Нет доступа"}), 403
    data = request.get_json(silent=True) or {}
    try:
        uah = int(data.get("uah_price", 800))
        uc = int(data.get("uc_price", 1320))
    except (ValueError, TypeError):
        return jsonify({"ok": False, "error": "Неверные данные"}), 400
    prices = {"uah_price": uah, "uc_price": uc}
    save_json(PRICES_FILE, prices)
    return jsonify({"ok": True, "prices": prices})


@app.route("/api/orders", methods=["GET"])
def get_orders():
    init_data = request.headers.get("X-Init-Data", "")
    if not is_admin(init_data):
        return jsonify({"ok": False, "error": "Нет доступа"}), 403
    orders = load_json(ORDERS_FILE, [])
    return jsonify({"ok": True, "orders": list(reversed(orders))})


@app.route("/api/orders/<order_id>/status", methods=["POST"])
def update_order_status(order_id):
    init_data = request.headers.get("X-Init-Data", "")
    if not is_admin(init_data):
        return jsonify({"ok": False, "error": "Нет доступа"}), 403
    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "")
    if new_status not in ("new", "in_progress", "done", "cancelled"):
        return jsonify({"ok": False, "error": "Неверный статус"}), 400
    with orders_lock():
        orders = load_json(ORDERS_FILE, [])
        found = False
        for o in orders:
            if o.get("id") == order_id:
                o["status"] = new_status
                found = True
                break
        if not found:
            return jsonify({"ok": False, "error": "Заказ не найден"}), 404
        save_json(ORDERS_FILE, orders)
    return jsonify({"ok": True})


@app.route("/api/order", methods=["POST"])
def create_order():
    init_data = request.headers.get("X-Init-Data", "")
    tg_user = verify_init_data(init_data)
    if not tg_user:
        return jsonify({"ok": False, "error": "Открой приложение через Telegram"}), 401

    # поддерживаем и multipart/form-data (с файлом), и application/json
    if request.content_type and "multipart/form-data" in request.content_type:
        payment_type = request.form.get("payment_type", "—")
        tg_tag = request.form.get("tg_tag", "—").strip()
        pubg_id = request.form.get("pubg_id", "").strip()
        screenshot_file = request.files.get("screenshot")
    else:
        data = request.get_json(silent=True) or {}
        payment_type = data.get("payment_type", "—")
        tg_tag = data.get("tg_tag", "—").strip()
        pubg_id = data.get("pubg_id", "").strip()
        screenshot_file = None

    if not tg_tag or tg_tag == "—":
        return jsonify({"ok": False, "error": "Telegram тег обязателен"}), 400

    user_name = (
        f"{tg_user.get('first_name', '')} {tg_user.get('last_name', '')}".strip()
        or "Неизвестно"
    )
    user_id = str(tg_user.get("id", "—"))

    prices = load_json(PRICES_FILE, {"uah_price": 800, "uc_price": 1320})
    price_label = (
        f"{prices['uah_price']} грн (Monobank)"
        if payment_type == "UAH"
        else f"{prices['uc_price']} UC"
    )

    order = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": int(time.time()),
        "user_name": user_name,
        "user_id": user_id,
        "tg_tag": tg_tag,
        "pubg_id": pubg_id,
        "payment_type": payment_type,
        "price_label": price_label,
        "status": "new",
    }

    with orders_lock():
        orders = load_json(ORDERS_FILE, [])
        orders.append(order)
        save_json(ORDERS_FILE, orders)

    if ADMIN_ID and BOT_TOKEN:
        caption_lines = [
            "🆕 <b>Новая заявка (Mini App)!</b>",
            f"🆔 ID: <code>{order['id']}</code>",
            f"👤 Клиент: {user_name} (TG ID: {user_id})",
            f"💰 Оплата: <b>{price_label}</b>",
            f"✈️ Telegram: <code>{tg_tag}</code>",
        ]
        if pubg_id and payment_type == "UAH":
            caption_lines.append(f"🎮 PUBG ID: <code>{pubg_id}</code>")
        caption = "\n".join(caption_lines)
        try:
            if screenshot_file:
                httpx.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    data={"chat_id": ADMIN_ID, "caption": caption, "parse_mode": "HTML"},
                    files={"photo": (screenshot_file.filename, screenshot_file.read(), screenshot_file.content_type)},
                    timeout=20,
                )
            else:
                httpx.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id": ADMIN_ID, "text": caption, "parse_mode": "HTML"},
                    timeout=10,
                )
        except Exception as e:
            print(f"Ошибка уведомления: {e}")

    return jsonify({"ok": True, "order_id": order["id"]})


# ─── Wheel API ───────────────────────────────────────────────────────────────

@app.route("/api/wheel/status", methods=["GET"])
def wheel_status():
    init_data = request.headers.get("X-Init-Data", "")
    user = verify_init_data(init_data)
    if not user:
        return jsonify({"ok": False, "error": "Открой приложение через Telegram"}), 401
    user_id = int(user.get("id", 0))
    now_ts = time.time()

    with get_db() as conn:
        row = conn.execute(
            "SELECT last_spin FROM wheel_spins WHERE user_id = ?", (user_id,)
        ).fetchone()
        can_spin = True
        seconds_left = 0
        if row:
            last_ts = datetime.fromisoformat(row["last_spin"]).timestamp()
            elapsed = now_ts - last_ts
            if elapsed < WHEEL_COOLDOWN:
                can_spin = False
                seconds_left = int(WHEEL_COOLDOWN - elapsed)

        now_iso = datetime.now().isoformat()
        promos = conn.execute(
            "SELECT code, discount, expires_at FROM wheel_promos "
            "WHERE user_id = ? AND used = 0 AND expires_at > ?",
            (user_id, now_iso),
        ).fetchall()

    return jsonify({
        "ok": True,
        "can_spin": can_spin,
        "seconds_left": seconds_left,
        "promos": [
            {"code": p["code"], "discount": p["discount"], "expires_at": p["expires_at"][:10]}
            for p in promos
        ],
    })


@app.route("/api/wheel/spin", methods=["POST"])
def do_wheel_spin():
    init_data = request.headers.get("X-Init-Data", "")
    user = verify_init_data(init_data)
    if not user:
        return jsonify({"ok": False, "error": "Открой приложение через Telegram"}), 401
    user_id = int(user.get("id", 0))
    now_dt = datetime.now()
    now_ts = now_dt.timestamp()

    promo_code = None
    result = None
    seg_index = 0

    conn = get_db()
    try:
        # BEGIN IMMEDIATE — эксклюзивная блокировка записи с самого начала,
        # исключает race condition при одновременных запросах от одного пользователя
        conn.execute("BEGIN IMMEDIATE")

        row = conn.execute(
            "SELECT last_spin FROM wheel_spins WHERE user_id = ?", (user_id,)
        ).fetchone()
        if row:
            last_ts = datetime.fromisoformat(row["last_spin"]).timestamp()
            if now_ts - last_ts < WHEEL_COOLDOWN:
                conn.rollback()
                conn.close()
                seconds_left = int(WHEEL_COOLDOWN - (now_ts - last_ts))
                return jsonify({"ok": False, "error": "Ещё рано крутить", "seconds_left": seconds_left}), 429

        result = _spin_result()
        seg_index = WHEEL_SEGMENTS.index(result)

        conn.execute(
            "INSERT OR REPLACE INTO wheel_spins (user_id, last_spin) VALUES (?, ?)",
            (user_id, now_dt.isoformat()),
        )

        if result["discount"] > 0:
            code = _gen_promo_code(result["discount"])
            expires_at = (now_dt + timedelta(days=3)).isoformat()
            conn.execute(
                "INSERT INTO wheel_promos (code, user_id, discount, created_at, expires_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (code, user_id, result["discount"], now_dt.isoformat(), expires_at),
            )
            promo_code = {
                "code": code,
                "discount": result["discount"],
                "expires_at": expires_at[:10],
            }

        conn.commit()
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        conn.close()
        print(f"[wheel/spin] Ошибка БД: {e}")
        return jsonify({"ok": False, "error": "Ошибка сервера"}), 500
    finally:
        conn.close()

    # Уведомление в Telegram: и админу и пользователю
    if promo_code and BOT_TOKEN:
        user_name = (
            f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            or "Пользователь"
        )
        admin_msg = (
            f"🎡 <b>Колесо фортуны!</b>\n"
            f"👤 {user_name} (ID: <code>{user_id}</code>) выиграл скидку <b>{promo_code['discount']}%</b>\n"
            f"🎟 Промокод: <code>{promo_code['code']}</code>\n"
            f"⏳ Действует до: {promo_code['expires_at']}"
        )
        user_msg = (
            f"🎡 Поздравляем! Ты выиграл скидку <b>{promo_code['discount']}%</b>!\n\n"
            f"🎟 Твой промокод: <code>{promo_code['code']}</code>\n"
            f"⏳ Действует до: {promo_code['expires_at']}\n\n"
            f"Покажи промокод при оформлении заказа в мини-приложении."
        )
        try:
            if ADMIN_ID:
                httpx.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id": ADMIN_ID, "text": admin_msg, "parse_mode": "HTML"},
                    timeout=10,
                )
            httpx.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": user_id, "text": user_msg, "parse_mode": "HTML"},
                timeout=10,
            )
        except Exception as e:
            print(f"[wheel] Ошибка уведомления: {e}")

    return jsonify({
        "ok": True,
        "segment_index": seg_index,
        "discount": result["discount"],
        "label": result["label"],
        "promo": promo_code,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
