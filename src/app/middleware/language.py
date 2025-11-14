import re
from typing import Dict, Any, Callable, Awaitable

import asyncpg
from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import Message, CallbackQuery
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
        if event.from_user.is_bot:
            print(f"⚠️ Skipping bot account: {event.from_user.id}")
            return
        manager_factory: BgManagerFactoryImpl = data.get("dialog_bg_factory")
        user_actions = UserDataBaseActions(pool=self.pool)

        try:
            user_data = await user_actions.get_user(event.from_user.id)
        except Exception as e:
            print(f"❌ Database error: {e}")
            return await handler(event, data)

        if user_data:
            data["lang"] = user_data[3]
            return await handler(event, data)

        if isinstance(event, CallbackQuery):
            return await handler(event, data)

        if not isinstance(event, Message):
            return await handler(event, data)

        referral_code = None
        if event.text:
            pattern = re.compile(r"^/start\s+([A-Za-z0-9]{10,20})$")
            match = pattern.match(event.text)
            if match:
                referral_code = match.group(1)
                print(f"🔗 Referral code detected: {referral_code}")

        try:
            manager = manager_factory.bg(
                data["bot"],
                event.from_user.id,
                chat_id=event.from_user.id
            )

            await manager.start(
                LanguageSelectionSG.Language_selection,
                data={"referral_code": referral_code} if referral_code else None,
                mode=StartMode.RESET_STACK,
                show_mode=ShowMode.DELETE_AND_SEND
            )

        except TelegramForbiddenError:
            print(f"⚠️ User {event.from_user.id} blocked bot or is a bot account")
            return

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return await handler(event, data)


