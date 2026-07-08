# ARMYAN SERVICES — Telegram Bot + Mini App

Telegram-бот и Flask мини-приложение для заказа услуг по PUBG MOBILE (настройка чувствительности, оплата UC и т.д.).

## Структура

- `bot.py` — Telegram-бот (polling, python-telegram-bot v22+)
- `webapp.py` — Flask мини-приложение (Telegram Mini App), порт 5000
- `templates/miniapp.html` — фронтенд мини-приложения
- `data/orders.json`, `data/prices.json` — файловое хранилище (с fcntl-локом, см. memory: orders-file-sharing)

## Запуск на Replit

Два воркфлоу:
- **Web App** — `python webapp.py` (порт 5000, webview)
- **Bot** — `python bot.py` (консоль, long polling)

Секреты (заданы в Replit Secrets):
- `TELEGRAM_BOT_TOKEN` — токен от @BotFather
- `ADMIN_CHAT_ID` — Telegram ID администратора

Переменные окружения:
- `WEBAPP_URL` — публичный URL мини-приложения (уже задан на dev-домен Replit)
- `REVIEWS_LINK` — опционально, ссылка на отзывы

## User preferences

- Language: Python
- Framework: python-telegram-bot (v22+), Flask
