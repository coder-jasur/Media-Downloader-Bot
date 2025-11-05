from pprint import pprint
from typing import Dict, Any, Callable, Awaitable

import asyncpg
from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram_dialog import StartMode, ShowMode
from aiogram_dialog.manager.bg_manager import BgManagerFactoryImpl

from src.app.database.queries.users import UserDataBaseActions
from src.app.states.language_selection import LanguageSelectionSG


class LanguageMiddleware(BaseMiddleware):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        manager_factory: BgManagerFactoryImpl = data.get("dialog_bg_factory")
        user_actions = UserDataBaseActions(pool=self.pool)

        try:
            user_data = await user_actions.get_user(event.from_user.id)
        except Exception as e:
            print(f"❌ Database error: {e}")
            return await handler(event, data)

        # User mavjud
        if user_data:
            data["lang"] = user_data[3]  # user_data[3] = language
            return await handler(event, data)

        # New user - show language selection
        # ⚠️ Skip CallbackQuery (ma'lumotga ega emas)
        if isinstance(event, CallbackQuery):
            return await handler(event, data)

        # Message event - start dialog
        if not isinstance(event, Message):
            return await handler(event, data)

        try:
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

        except TelegramForbiddenError:
            print(f"⚠️ User {event.from_user.id} blocked bot")
            # Bot xabar yubora olmadi - dialog skip
            return

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return await handler(event, data)



