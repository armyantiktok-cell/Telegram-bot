# ARMYAN SERVICES — Telegram Bot

Telegram-бот и мини-приложение для заказа услуг по PUBG MOBILE.

## Структура

| Файл | Описание |
|------|----------|
| `bot.py` | Telegram-бот (polling) |
| `webapp.py` | Flask мини-приложение (Mini App) |
| `templates/miniapp.html` | Фронтенд мини-приложения |
| `data/orders.json` | База заказов |
| `data/prices.json` | Актуальные цены |

## Деплой на Railway

### 1. Создай два сервиса в одном проекте

Railway запускает оба процесса из `Procfile`:
- `web` — мини-приложение Flask (получает публичный URL)
- `worker` — Telegram-бот (polling, не требует URL)

**Способ:** подключи GitHub-репозиторий → Railway подхватит `Procfile` автоматически.

### 2. Переменные окружения

Задай в настройках сервиса (Variables):

| Переменная | Обязательная | Описание |
|------------|:---:|---------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Токен от @BotFather |
| `ADMIN_CHAT_ID` | ✅ | Твой Telegram ID (узнать у @userinfobot) |
| `WEBAPP_URL` | ✅ | Публичный URL `web`-сервиса на Railway |
| `REVIEWS_LINK` | ❌ | Ссылка на канал с отзывами (по умолчанию https://t.me/ARMYANua) |

> ⚠️ `WEBAPP_URL` станет известен **после первого деплоя** `web`-сервиса.  
> Сначала задеплой, скопируй URL, вставь в переменную — бот подхватит при следующем рестарте.

### 3. Персистентные данные

`data/orders.json` и `data/prices.json` хранятся в файловой системе контейнера.  
Railway **сбрасывает файлы при каждом деплое** — для продакшена подключи Railway Volume:

```
Railway Dashboard → твой сервис → Volumes → Add Volume → путь: /app/data
```

### Локальный запуск

```bash
pip install -r requirements.txt

# В одном терминале:
python bot.py

# В другом:
python webapp.py
```

Создай `.env` по образцу `.env.example` и задай нужные переменные.
