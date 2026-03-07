import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{CONFIG_DIR / 'pb_bi.db'}"

SECRET_KEY = os.getenv("SECRET_KEY", "pb-bi-secret-key-change-in-production")

LLM_API_KEY = os.getenv("LLM_API_KEY", "sk-mkmyqqpvogvoarlcqvxisouozxicrjvvvdmceqtaxccfwcyg")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-V3")
