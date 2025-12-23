import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from http.server import BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from dotenv import load_dotenv

load_dotenv()

from bot.config import config
from bot.handlers import setup_routers
from bot.middlewares import setup_middlewares

bot = Bot(token=config.bot.token)
dp = Dispatcher()

setup_routers_done = False


async def init_dispatcher():
    global setup_routers_done
    if not setup_routers_done:
        router = setup_routers()
        dp.include_router(router)
        await setup_middlewares(dp)
        setup_routers_done = True


async def process_update(update_data: dict):
    await init_dispatcher()
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
