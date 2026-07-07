import os
import httpx
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_ID = os.environ.get("ADMIN_CHAT_ID", "")
MONOBANK_CARD = "4441 1111 3196 2080"
PUBG_ID_FOR_UC = "51230579110"


@app.route("/")
def index():
    return render_template(
        "miniapp.html",
        monobank_card=MONOBANK_CARD,
        pubg_id_uc=PUBG_ID_FOR_UC,
    )


@app.route("/api/order", methods=["POST"])
def create_order():
    data = request.get_json(silent=True) or {}
    payment_type = data.get("payment_type", "—")
    discord = data.get("discord", "—").strip()
    pubg_id = data.get("pubg_id", "—").strip()
    user_name = data.get("user_name", "—")
    user_id = data.get("user_id", "—")

    if not discord:
        return jsonify({"ok": False, "error": "Discord обязателен"}), 400

    if ADMIN_ID and BOT_TOKEN:
        lines = [
            "🆕 <b>Новая заявка (Mini App)!</b>",
            f"👤 Клиент: {user_name} (ID: {user_id})",
            f"💰 Оплата: <b>{'800 грн (Monobank)' if payment_type == 'UAH' else '1320 UC'}</b>",
            f"🎮 Discord: <code>{discord}</code>",
        ]
        if pubg_id and pubg_id != "—" and payment_type == "UAH":
            lines.append(f"🆔 PUBG ID: <code>{pubg_id}</code>")
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

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
