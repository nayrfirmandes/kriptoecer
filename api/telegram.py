import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from http.server import BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from prisma import Prisma

load_dotenv()

from bot.config import config
from bot.handlers import setup_routers
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.middlewares.database import DatabaseMiddleware
from bot.middlewares.user_status import UserStatusMiddleware
from bot.middlewares.logging import LoggingMiddleware

bot = None
dp = None
prisma = None
initialized = False


async def init():
    global bot, dp, prisma, initialized
    
    if initialized:
        return
    
    prisma = Prisma()
    await prisma.connect()
    
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
    
    initialized = True


async def process_update(update_data: dict):
    await init()
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
