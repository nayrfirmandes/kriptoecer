import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class BotConfig:
    token: str
    admin_ids: list[int]


@dataclass
class DatabaseConfig:
    url: str


@dataclass
class OxaPayConfig:
    api_key: str
    merchant_id: str
    webhook_secret: str
    base_url: str = "https://api.oxapay.com"


@dataclass
class AppConfig:
    bot: BotConfig
    database: DatabaseConfig
    oxapay: OxaPayConfig
    debug: bool = False


def load_config() -> AppConfig:
    admin_ids_str = os.getenv("ADMIN_TELEGRAM_IDS", "")
    admin_ids = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
    
    return AppConfig(
        bot=BotConfig(
            token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            admin_ids=admin_ids,
        ),
        database=DatabaseConfig(
            url=os.getenv("DATABASE_URL", ""),
        ),
        oxapay=OxaPayConfig(
            api_key=os.getenv("OXAPAY_API_KEY", ""),
            merchant_id=os.getenv("OXAPAY_MERCHANT_ID", ""),
            webhook_secret=os.getenv("OXAPAY_WEBHOOK_SECRET", ""),
        ),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )


config = load_config()
