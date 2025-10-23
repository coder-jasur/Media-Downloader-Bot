import asyncio
import logging
import os

import asyncpg
from aiogram import Dispatcher, Bot, Router
from aiogram.client.default import DefaultBotProperties
from aiogram_dialog import setup_dialogs

from logs.loggger_conf import setup_logging
from src.app.common.bot_commands import bot_commands
from src.app.common.db_url import construct_postgresql_url
from src.app.core.config import Settings
from src.app.database.tables import create_database_tables
from src.app.dialogs import register_all_dialogs
from src.app.handlers import register_all_router
from src.app.middleware import register_middleware

logger = logging.getLogger(__name__)


async def main():
    settings = Settings()

    dsn = construct_postgresql_url(settings)

    pool = await asyncpg.create_pool(
        dsn,
    )
    async with pool.acquire() as conn:
        await create_database_tables(conn)

    dp = Dispatcher()
    dialogs_router = Router()
    register_all_dialogs(dialogs_router)
    dp.include_router(dialogs_router)
    register_all_router(dp, settings)
    register_middleware(dp, settings, pool)
    setup_dialogs(dp)

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode="HTML"))

    await bot_commands(bot, settings)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        setup_logging("logs/logger.yml")
        os.makedirs("media", exist_ok=True)
        os.makedirs("./media/videos", exist_ok=True)
        os.makedirs("./media/audios", exist_ok=True)
        os.makedirs("./media/photos", exist_ok=True)
        asyncio.run(main())
    except Exception as e:
        logger.exception(e)
