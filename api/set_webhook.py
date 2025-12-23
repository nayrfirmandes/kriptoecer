import os
import sys

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import asyncio
import json
from http.server import BaseHTTPRequestHandler

from dotenv import load_dotenv

load_dotenv()


async def set_telegram_webhook(host: str):
    from aiogram import Bot
    
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    bot = Bot(token=token)
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
