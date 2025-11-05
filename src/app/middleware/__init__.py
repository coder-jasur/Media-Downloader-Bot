import asyncpg
from aiogram import Dispatcher

from src.app.core.config import Settings
from src.app.middleware.database_pool import DatabaseMiddleware
from src.app.middleware.language import LanguageMiddleware
from src.app.middleware.settings import SettingsMiddleware


def register_middleware(dp: Dispatcher, settings_: Settings, pool: asyncpg.Pool):


    language_middleware = LanguageMiddleware(pool)
    dp.message.outer_middleware(language_middleware)
    dp.callback_query.outer_middleware(language_middleware)
    dp.chat_member.outer_middleware(language_middleware)

    settings_middleware = SettingsMiddleware(settings_)
    dp.message.outer_middleware(settings_middleware)
    dp.callback_query.outer_middleware(settings_middleware)
    dp.chat_member.outer_middleware(settings_middleware)

    database_pool = DatabaseMiddleware(pool)
    dp.message.outer_middleware(database_pool)
    dp.callback_query.outer_middleware(database_pool)
