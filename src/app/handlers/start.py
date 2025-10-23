import asyncpg
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asyncpg import Connection

from src.app.texts import user_texts
from src.app.database.queries.referals import RefferralActions
from src.app.database.queries.users import UserActions


start_router = Router()


@start_router.message(CommandStart())
async def command_start(message: Message, lang: str):
    await message.answer(text=user_texts["start"][lang])


@start_router.message(CommandStart(magic=F.args.regexp(r"^[a-z0-9]{10}$")))
async def on_message_with_args(
    message: Message,
    command: CommandObject,
    pool: asyncpg.Pool,
    state: FSMContext,
    lang: str
) -> None:
    await state.clear()
    user_actions = UserActions(pool)
    referrals_actions = RefferralActions(pool)
    user = await user_actions.get_user(message.from_user.id)

    if not user:
        await referrals_actions.increment_referal_members_count(
            referral_id=command.args
        )

    await message.answer(text=user_texts["start"][lang])
