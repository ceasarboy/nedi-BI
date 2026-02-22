import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{CONFIG_DIR / 'pb_bi.db'}"

SECRET_KEY = os.getenv("SECRET_KEY", "pb-bi-secret-key-change-in-production")
