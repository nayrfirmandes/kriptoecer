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
    
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.3))
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))
    
    dp.message.middleware(DatabaseMiddleware(prisma))
    dp.callback_query.middleware(DatabaseMiddleware(prisma))
    
    dp.message.middleware(UserStatusMiddleware())
    dp.callback_query.middleware(UserStatusMiddleware())
    
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
