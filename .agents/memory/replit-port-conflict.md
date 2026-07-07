---
name: duplicate external port 80 mapping
description: stale port mapping from mockup sandbox can hijack externalPort 80 and cause 502 on the public dev URL
---

Symptom: app works on localhost:5000 but the public `$REPLIT_DEV_DOMAIN` returns 502 (Telegram Mini App fails to open).

**Why:** Creating a mockup-sandbox artifact can add a second `[[ports]]` mapping (e.g. 23636 → 80) to `.replit`, conflicting with 5000 → 80. The proxy then routes external traffic to the dead sandbox port.

**How to apply:** `.replit` cannot be edited directly. Fix by re-running `configureWorkflow({name, command, waitForPort: 5000, outputType: "webview"})` via code_execution — it rewrites port mappings and removes the stale entry. Verify with `curl -o /dev/null -w "%{http_code}" https://$REPLIT_DEV_DOMAIN/` → expect 200.
