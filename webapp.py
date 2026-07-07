import os
import hmac
import hashlib
import json
import time
import uuid
import httpx
from pathlib import Path
from urllib.parse import parse_qsl
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))
EXTRA_ADMIN_IDS = [1440236609]
ADMIN_IDS = {i for i in [ADMIN_ID, *EXTRA_ADMIN_IDS] if i > 0}
MONOBANK_CARD = "4441 1111 3196 2080"
PUBG_ID_FOR_UC = "51230579110"
REVIEWS_LINK = os.environ.get("REVIEWS_LINK", "https://t.me/ARMYANua")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
ORDERS_FILE = DATA_DIR / "orders.json"
PRICES_FILE = DATA_DIR / "prices.json"


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


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

    data = request.get_json(silent=True) or {}
    payment_type = data.get("payment_type", "—")
    tg_tag = data.get("tg_tag", "—").strip()
    pubg_id = data.get("pubg_id", "").strip()
    user_name = (
        f"{tg_user.get('first_name', '')} {tg_user.get('last_name', '')}".strip()
        or "Неизвестно"
    )
    user_id = str(tg_user.get("id", "—"))

    if not tg_tag or tg_tag == "—":
        return jsonify({"ok": False, "error": "Telegram тег обязателен"}), 400

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

    orders = load_json(ORDERS_FILE, [])
    orders.append(order)
    save_json(ORDERS_FILE, orders)

    if ADMIN_ID and BOT_TOKEN:
        lines = [
            "🆕 <b>Новая заявка (Mini App)!</b>",
            f"🆔 ID: <code>{order['id']}</code>",
            f"👤 Клиент: {user_name} (TG ID: {user_id})",
            f"💰 Оплата: <b>{price_label}</b>",
            f"✈️ Telegram: <code>{tg_tag}</code>",
        ]
        if pubg_id and payment_type == "UAH":
            lines.append(f"🎮 PUBG ID: <code>{pubg_id}</code>")
        lines.append("\n📸 Клиент отправит скриншот оплаты в бот.")
        try:
            httpx.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": ADMIN_ID,
                    "text": "\n".join(lines),
                    "parse_mode": "HTML",
                },
                timeout=10,
            )
        except Exception as e:
            print(f"Ошибка уведомления: {e}")

    return jsonify({"ok": True, "order_id": order["id"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
