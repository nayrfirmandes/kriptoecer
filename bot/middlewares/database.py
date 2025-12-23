from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from prisma import Prisma


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, prisma: Prisma):
        self.prisma = prisma
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["db"] = self.prisma
        return await handler(event, data)
