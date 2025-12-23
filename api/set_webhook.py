import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from http.server import BaseHTTPRequestHandler

from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

from bot.config import config


async def set_telegram_webhook(host: str):
    bot = Bot(token=config.bot.token)
    webhook_url = f"https://{host}/telegram/webhook"
    
    await bot.set_webhook(webhook_url)
    await bot.session.close()
    
    return {"ok": True, "webhook_url": webhook_url}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        host = self.headers.get('Host', '')
        
        try:
            result = asyncio.run(set_telegram_webhook(host))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            print(f"Error setting webhook: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
