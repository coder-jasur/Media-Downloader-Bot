import re

import asyncpg
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asyncpg import Connection

from src.app.database.queries.referals import ReferalDataBaseActions
from src.app.database.queries.users import UserDataBaseActions
from src.app.utils.i18n import get_translator

start_router = Router()


@start_router.message(CommandStart())
async def command_start(message: Message, lang: str):
    _ = get_translator(lang).gettext
    await message.answer(
        text=_("Start text").format(
            message.from_user.first_name
            or message.from_user.last_name
            or message.from_user.username
        )
    )
