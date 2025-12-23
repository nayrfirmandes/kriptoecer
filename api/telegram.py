import os
import sys
import subprocess

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import asyncio
import json
from http.server import BaseHTTPRequestHandler
from dotenv import load_dotenv

load_dotenv()

_bot = None
_dp = None
_prisma = None
_initialized = False


def ensure_prisma_generated():
    try:
        subprocess.run(
            ["python", "-m", "prisma", "generate"],
            check=True,
            capture_output=True,
            cwd=root_path
        )
    except Exception as e:
        print(f"Prisma generate error: {e}")


def get_config():
    from dataclasses import dataclass
    
    @dataclass
    class Config:
        token: str
        admin_ids: list
    
    admin_ids_str = os.getenv("ADMIN_TELEGRAM_IDS", "")
    admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()]
    
    return Config(
        token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        admin_ids=admin_ids,
    )


async def init():
    global _bot, _dp, _prisma, _initialized
    
    if _initialized:
        return _bot, _dp
    
    ensure_prisma_generated()
    
    from prisma import Prisma
    from aiogram import Bot, Dispatcher
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.fsm.storage.memory import MemoryStorage
    
    config = get_config()
    
    _prisma = Prisma()
    await _prisma.connect()
    
    _bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    
    storage = MemoryStorage()
    _dp = Dispatcher(storage=storage)
    
    from bot.handlers import setup_routers
    from bot.middlewares.throttling import ThrottlingMiddleware
    from bot.middlewares.database import DatabaseMiddleware
    from bot.middlewares.user_status import UserStatusMiddleware
    from bot.middlewares.logging import LoggingMiddleware
    
    logging_mw = LoggingMiddleware()
    throttling_mw = ThrottlingMiddleware(rate_limit=0.1)
    database_mw = DatabaseMiddleware(_prisma)
    user_status_mw = UserStatusMiddleware()
    
    _dp.message.middleware(logging_mw)
    _dp.callback_query.middleware(logging_mw)
    _dp.message.middleware(throttling_mw)
    _dp.callback_query.middleware(throttling_mw)
    _dp.message.middleware(database_mw)
    _dp.callback_query.middleware(database_mw)
    _dp.message.middleware(user_status_mw)
    _dp.callback_query.middleware(user_status_mw)
    
    router = setup_routers()
    _dp.include_router(router)
    
    _initialized = True
    return _bot, _dp


async def process_update(update_data: dict):
    from aiogram.types import Update
    bot, dp = await init()
    update = Update(**update_data)
    await dp.feed_update(bot, update)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            update_data = json.loads(body.decode('utf-8'))
            asyncio.run(process_update(update_data))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
        except Exception as e:
            print(f"Error processing update: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "ok", "service": "telegram-webhook"}')
