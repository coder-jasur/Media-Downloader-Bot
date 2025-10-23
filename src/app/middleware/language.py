from pprint import pprint
from typing import Dict, Any, Callable, Awaitable

import asyncpg
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram_dialog import StartMode, ShowMode
from aiogram_dialog.manager.bg_manager import BgManagerFactoryImpl

from src.app.database.queries.users import UserActions
from src.app.states.language_selection import LanguageSelectionSG


class LanguageMiddleware(BaseMiddleware):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ):
        manager_factory: BgManagerFactoryImpl = data.get("dialog_bg_factory")

        user_actions = UserActions(pool=self.pool)
        user_data = await user_actions.get_user(event.from_user.id)

        if not user_data:
            if isinstance(event, CallbackQuery):
                return await handler(event, data)

            manager = manager_factory.bg(
                data["bot"],
                event.from_user.id,
                chat_id=event.from_user.id
            )
            await manager.start(
                LanguageSelectionSG.Language_selection,
                mode=StartMode.RESET_STACK,
                show_mode=ShowMode.DELETE_AND_SEND
            )
            return

        data["lang"] = user_data[3]
        return await handler(event, data)



