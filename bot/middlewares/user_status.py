from typing import Any, Awaitable, Callable, Dict
from datetime import datetime, timedelta, timezone
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from prisma import Prisma


class UserStatusMiddleware(BaseMiddleware):
    INACTIVE_MONTHS = 6
    ACTIVITY_UPDATE_INTERVAL = 3600
    
    def __init__(self):
        super().__init__()
        self._last_activity_cache: Dict[int, datetime] = {}
    
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
        
        if not user_id:
            return await handler(event, data)
        
        now = datetime.now(timezone.utc)
        cached_time = self._last_activity_cache.get(user_id)
        
        if cached_time and (now - cached_time).total_seconds() < self.ACTIVITY_UPDATE_INTERVAL:
            return await handler(event, data)
        
        user = await db.user.find_unique(where={"telegramId": user_id})
        
        if user:
            inactive_threshold = now - timedelta(days=self.INACTIVE_MONTHS * 30)
            
            last_active = user.lastActiveAt
            if last_active.tzinfo is None:
                last_active = last_active.replace(tzinfo=timezone.utc)
            
            if last_active < inactive_threshold and user.status == "ACTIVE":
                await db.user.update(
                    where={"id": user.id},
                    data={"status": "INACTIVE"}
                )
            else:
                if (now - last_active).total_seconds() >= self.ACTIVITY_UPDATE_INTERVAL:
                    await db.user.update(
                        where={"id": user.id},
                        data={"lastActiveAt": now}
                    )
            
            self._last_activity_cache[user_id] = now
            data["user"] = user
        
        return await handler(event, data)
