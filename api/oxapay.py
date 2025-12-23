import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
import hmac
import hashlib
from http.server import BaseHTTPRequestHandler
from decimal import Decimal

from dotenv import load_dotenv

load_dotenv()

from bot.config import config


async def process_oxapay_webhook(data: dict):
    from prisma import Prisma
    
    db = Prisma()
    await db.connect()
    
    try:
        track_id = data.get("trackId", "")
        status = data.get("status", "")
        
        if not track_id:
            return {"ok": False, "error": "No trackId"}
        
        order = await db.cryptoorder.find_unique(where={"oxapayTrackId": track_id})
        
        if not order:
            return {"ok": False, "error": "Order not found"}
        
        if status == "Paid" and order.status == "PENDING":
            await db.cryptoorder.update(
                where={"id": order.id},
                data={"status": "COMPLETED"}
            )
        elif status == "Expired" and order.status == "PENDING":
            await db.cryptoorder.update(
                where={"id": order.id},
                data={"status": "FAILED"}
            )
            
            await db.balance.update(
                where={"userId": order.userId},
                data={"amount": {"increment": order.totalIdr}}
            )
        
        return {"ok": True}
    finally:
        await db.disconnect()


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    if not secret:
        return True
    
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        signature = self.headers.get('HMAC', '')
        
        if not verify_signature(body, signature, config.oxapay.webhook_secret):
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": false, "error": "Invalid signature"}')
            return
        
        try:
            data = json.loads(body.decode('utf-8'))
            result = asyncio.run(process_oxapay_webhook(data))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            print(f"Error processing OxaPay webhook: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "ok", "service": "oxapay-webhook"}')
