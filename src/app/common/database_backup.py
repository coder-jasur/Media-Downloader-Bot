import logging

import aiofiles
import asyncpg
from aiogram.types import FSInputFile
import os
import asyncio
import datetime
from aiogram import Bot

from src.app.database.queries.users import UserDataBaseActions

logger = logging.getLogger(__name__)


async def send_database_to_owner(bot: Bot, chat_ids: list[int], db_path: str):
    is_file_exists = await asyncio.to_thread(os.path.exists, db_path)

    if is_file_exists:
        db_file = FSInputFile(db_path)
        tasks = [
            asyncio.create_task(
                bot.send_document(
                    chat_id=chat_id, document=db_file, caption="DataBase"
                )
            )
            for chat_id in chat_ids
        ]
        await asyncio.gather(*tasks)


async def daily_database_sender(bot: Bot, chat_ids: list[int], pool: asyncpg.Pool) -> None:
    while True:
        try:
            user_actions = UserDataBaseActions(pool)
            all_users = await user_actions.get_all_user()

            async with aiofiles.open("all_users.txt", "w", encoding="utf-8") as f:
                for user in all_users:
                    await f.write(f"{user}\n")

            now = datetime.datetime.now()
            target_time = now.replace(hour=0, minute=0, second=0, microsecond=0)

            if now >= target_time:
                target_time += datetime.timedelta(days=1)

            sleep_duration = (target_time - now).total_seconds()
            await asyncio.sleep(sleep_duration)

            await send_database_to_owner(bot, chat_ids, "all_users.txt")

        except Exception as e:
            logger.exception(e)


