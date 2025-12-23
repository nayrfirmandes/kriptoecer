from typing import Any, Awaitable, Callable, Dict
from datetime import datetime, timedelta, timezone
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from prisma import Prisma


class UserStatusMiddleware(BaseMiddleware):
    INACTIVE_MONTHS = 6
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        db: Prisma = data.get("db")
        
        if not db:
            return await handler(event, data)
        
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
        
        if user_id:
            user = await db.user.find_unique(where={"telegramId": user_id})
            
            if user:
                now = datetime.now(timezone.utc)
                inactive_threshold = now - timedelta(days=self.INACTIVE_MONTHS * 30)
                
                last_active = user.lastActiveAt
                if last_active.tzinfo is None:
                    last_active = last_active.replace(tzinfo=timezone.utc)
                
                if last_active < inactive_threshold and user.status == "ACTIVE":
                    await db.user.update(
                        where={"id": user.id},
                        data={"status": "INACTIVE"}
                    )
                    user = await db.user.find_unique(where={"id": user.id})
                else:
                    await db.user.update(
                        where={"id": user.id},
                        data={"lastActiveAt": now}
                    )
                
                data["user"] = user
        
        return await handler(event, data)
