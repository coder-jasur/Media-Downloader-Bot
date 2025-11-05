from typing import Callable, Dict, Any, Awaitable

import asyncpg
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def __call__(
        self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:

        data["pool"] = self.pool
        return await handler(event, data)