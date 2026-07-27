

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


DB_PATH = str(DATA_DIR / "detox.db")


def _load_dotenv() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()


def _int(name: str, default: int = 0) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


HUB_TOKEN = os.environ.get("HUB_TOKEN", "")
TRADE_TOKEN = os.environ.get("TRADE_TOKEN", "")
ESCORT_TOKEN = os.environ.get("ESCORT_TOKEN", "")
DRAW_TOKEN = os.environ.get("DRAW_TOKEN", "")


ADMINS = [int(x) for x in os.environ.get("ADMINS", "6059673725").split(",") if x.strip()]


OWNERS = [int(x) for x in os.environ.get("OWNERS", "6059673725,8699517479").split(",") if x.strip()]
HUB_DB_PATH = os.environ.get("HUB_DB_PATH", "/root/eternal/OnyxPay/bot_database.db")


TRADE_BOT_USERNAME = os.environ.get("TRADE_BOT_USERNAME", "DemoTradeBot")
ESCORT_BOT_USERNAME = os.environ.get("ESCORT_BOT_USERNAME", "DemoEscortBot")
DRAW_BOT_USERNAME = os.environ.get("DRAW_BOT_USERNAME", "DemoDrawBot")


LINK_CHAT = os.environ.get("LINK_CHAT", "https://t.me/")
LINK_INFO = os.environ.get("LINK_INFO", "https://t.me/")
LINK_PROFITS = os.environ.get("LINK_PROFITS", "https://t.me/")
LINK_RULES = os.environ.get("LINK_RULES", "https://telegra.ph/")
LINK_MANUALS = os.environ.get("LINK_MANUALS", "https://t.me/")
LINK_FINANCE = os.environ.get("LINK_FINANCE", "https://t.me/")


DTC_PER_1000_RUB = float(os.environ.get("DTC_PER_1000_RUB", "1.0"))
PAYOUT_DEPOSIT = _int("PAYOUT_DEPOSIT", 80)
PAYOUT_WITH_TP = _int("PAYOUT_WITH_TP", 70)

PROJECT_OPENED = os.environ.get("PROJECT_OPENED", "06.12.2025")


PROJECT_NAME = os.environ.get("PROJECT_NAME", "Onyx Hub")

HUB_BOT_USERNAME = os.environ.get("HUB_BOT_USERNAME", "aOnyxPay_Bot")


def require_token(token: str, name: str) -> str:
    if not token:
        raise SystemExit(
            f"[DETOX] Не задан {name}. Создай бота в @BotFather и впиши токен в /root/detox/.env"
        )
    return token
