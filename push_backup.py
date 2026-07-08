#!/usr/bin/env python3
"""
Скрипт восстановления бэкапа базы данных мини-приложения.

Использование:
  python push_backup.py <путь_к_бэкапу>

Пример:
  python push_backup.py data/backups/miniapp_2026-07-08_13_00.db

Без аргумента — покажет список доступных бэкапов.
"""
import sys
import shutil
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
BACKUP_DIR = DATA_DIR / "backups"
DB_FILE = DATA_DIR / "miniapp.db"


def list_backups():
    backups = sorted(BACKUP_DIR.glob("miniapp_*.db"), reverse=True)
    if not backups:
        print("❌ Бэкапов не найдено в", BACKUP_DIR)
        return
    print(f"📦 Доступные бэкапы ({len(backups)} шт.):\n")
    for b in backups:
        size_kb = b.stat().st_size // 1024
        print(f"  {b.name}  ({size_kb} KB)")
    print(f"\nДля восстановления запусти:\n  python push_backup.py data/backups/<имя_файла>")


def restore(src_path: str):
    src = Path(src_path)
    if not src.exists():
        print(f"❌ Файл не найден: {src}")
        sys.exit(1)
    if not src.name.endswith(".db"):
        print("❌ Файл должен быть .db")
        sys.exit(1)

    # Сделаем авто-бэкап текущей БД перед заменой
    if DB_FILE.exists():
        ts = datetime.now().strftime("%Y-%m-%d_%H_%M")
        auto_bak = BACKUP_DIR / f"miniapp_{ts}_before_restore.db"
        BACKUP_DIR.mkdir(exist_ok=True)
        shutil.copy2(str(DB_FILE), str(auto_bak))
        print(f"💾 Текущая БД сохранена как: {auto_bak.name}")

    shutil.copy2(str(src), str(DB_FILE))
    print(f"✅ Восстановлено: {src.name}  →  {DB_FILE}")
    print("🔄 Перезапусти webapp.py чтобы изменения вступили в силу.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        list_backups()
    else:
        restore(sys.argv[1])
