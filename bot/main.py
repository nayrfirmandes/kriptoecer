import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from prisma import Prisma

from bot.config import config
from bot.handlers import setup_routers
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.middlewares.database import DatabaseMiddleware
from bot.middlewares.user_status import UserStatusMiddleware
from bot.middlewares.logging import LoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    if not config.bot.token:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        return
    
    if not config.database.url:
        logger.error("BOT_DATABASE is not set!")
        return
    
    prisma = Prisma()
    await prisma.connect()
    logger.info("Connected to database")
    
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    logging_mw = LoggingMiddleware()
    throttling_mw = ThrottlingMiddleware(rate_limit=0.1)
    database_mw = DatabaseMiddleware(prisma)
    user_status_mw = UserStatusMiddleware()
    
    dp.message.middleware(logging_mw)
    dp.callback_query.middleware(logging_mw)
    
    dp.message.middleware(throttling_mw)
    dp.callback_query.middleware(throttling_mw)
    
    dp.message.middleware(database_mw)
    dp.callback_query.middleware(database_mw)
    
    dp.message.middleware(user_status_mw)
    dp.callback_query.middleware(user_status_mw)
    
    router = setup_routers()
    dp.include_router(router)
    
    logger.info("Starting bot...")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await prisma.disconnect()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
