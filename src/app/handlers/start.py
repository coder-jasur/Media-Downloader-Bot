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

@start_router.message(CommandStart(magic=F.args.regexp(r"^[a-z0-9]{10}$")))
async def on_message_with_args(
    message: Message,
    command: CommandObject,
    pool: asyncpg.Pool,
    state: FSMContext,
    lang: str
) -> None:
    await state.clear()
    user_actions = UserDataBaseActions(pool)
    referrals_actions = ReferalDataBaseActions(pool)
    user = await user_actions.get_user(message.from_user.id)

    if not user:
        await referrals_actions.increment_referal_members_count(
            referral_id=command.args
        )
    _ = get_translator(lang).gettext
    await message.answer(text=_("Start text").format(message.from_user.first_name))


@start_router.message(CommandStart())
async def command_start(message: Message, lang: str):
    _ = get_translator(lang).gettext
    await message.answer(text=_("Start text").format(message.from_user.first_name))



