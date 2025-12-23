import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from prisma import Prisma

from bot.config import config
from bot.handlers import setup_routers
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.middlewares.database import DatabaseMiddleware
from bot.middlewares.user_status import UserStatusMiddleware
from bot.middlewares.logging import LoggingMiddleware
from bot.webhook import handle_oxapay_webhook, health_check

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/telegram/webhook")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "5000"))


def setup_dispatcher(prisma: Prisma) -> Dispatcher:
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
    
    return dp


async def on_startup(bot: Bot):
    webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
    )
    logger.info(f"Webhook set to: {webhook_url}")


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    logger.info("Webhook deleted")


async def run_webhook_mode(prisma: Prisma):
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    dp = setup_dispatcher(prisma)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    app = web.Application()
    app["db"] = prisma
    app["bot"] = bot
    
    app.router.add_post("/webhook/oxapay", handle_oxapay_webhook)
    app.router.add_get("/health", health_check)
    
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    
    setup_application(app, dp, bot=bot)
    
    logger.info(f"Starting webhook server on port {WEBHOOK_PORT}")
    logger.info(f"Telegram webhook path: {WEBHOOK_PATH}")
    logger.info(f"OxaPay webhook path: /webhook/oxapay")
    logger.info(f"Admin IDs: {config.bot.admin_ids}")
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
    await site.start()
    
    logger.info("Bot is running in WEBHOOK mode!")
    
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
        await bot.session.close()


async def run_polling_mode(prisma: Prisma):
    from bot.webhook import run_webhook_server
    
    webhook_runner = await run_webhook_server(prisma, port=8080)
    
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    dp = setup_dispatcher(prisma)
    
    logger.info("Starting Crypto Trading Bot in POLLING mode...")
    logger.info(f"Admin IDs: {config.bot.admin_ids}")
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await webhook_runner.cleanup()
        await bot.session.close()


async def main():
    if not config.bot.token:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        logger.info("Please set TELEGRAM_BOT_TOKEN environment variable")
        return
    
    if not config.database.url:
        logger.error("DATABASE_URL is not set!")
        logger.info("Please set DATABASE_URL environment variable")
        return
    
    prisma = Prisma()
    
    try:
        await prisma.connect()
        logger.info("Connected to database")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        logger.info("Please check DATABASE_URL and ensure database is accessible")
        return
    
    try:
        if WEBHOOK_URL:
            await run_webhook_mode(prisma)
        else:
            await run_polling_mode(prisma)
    finally:
        await prisma.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
