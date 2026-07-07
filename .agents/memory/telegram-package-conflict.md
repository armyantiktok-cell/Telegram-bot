---
name: telegram package conflict
description: pip installs can break python-telegram-bot imports via stale `telegram` package dir
---

After any pip install (e.g. Flask), the bot may fail with `ImportError: cannot import name 'Update' from 'telegram'`.

**Why:** A stale/stub `telegram` package directory in `.pythonlibs/lib/python3.11/site-packages/telegram` shadows python-telegram-bot. Happened twice in this project.

**How to apply:** Fix with:
```
rm -rf .pythonlibs/lib/python3.11/site-packages/telegram && pip install python-telegram-bot --force-reinstall -q
```
Then verify `python3 -c "from telegram import Update"` before restarting the bot workflow.
