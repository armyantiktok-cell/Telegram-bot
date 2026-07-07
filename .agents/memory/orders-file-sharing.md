---
name: Shared orders.json between bot and mini app
description: Bot and Flask webapp both write data/orders.json — must use the fcntl lock + atomic write pattern
---

The Telegram bot (bot.py) and the Flask mini app (webapp.py) run as separate processes and both read-modify-write `data/orders.json`.

**Rule:** any write to orders must go through the shared pattern: exclusive `fcntl.flock` on `data/orders.lock`, then write to a temp file and `replace()` (atomic). Admin decisions must be idempotent — terminal statuses (`done`, `cancelled`) are never overwritten (bot's `set_order_status` returns `already`).

**Why:** concurrent writes silently lost orders/status changes, and double-clicks on the admin «Готово/Отклонить» buttons could flip status and send contradictory client messages.

**How to apply:** when adding any new order-writing endpoint or handler in either process, wrap the read-modify-write in the lock helper and keep the terminal-status guard.
