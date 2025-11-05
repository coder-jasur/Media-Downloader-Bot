import asyncpg
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery

from src.app.database.queries.channels import ChannelDataBaseActions
from src.app.filters.chek_channel_sub import CheckSubscription
from src.app.keyboards.inline import not_channels_button
from src.app.utils.i18n import get_translator

check_channel_sub_router = Router()
check_channel_sub_router.message.filter(CheckSubscription())
check_channel_sub_router.callback_query.filter(CheckSubscription())


@check_channel_sub_router.message()
async def check_channel_sub_message(message: Message, pool: asyncpg.Pool, bot: Bot, lang: str):
    channel_actions = ChannelDataBaseActions(pool)
    channel_data = await channel_actions.get_all_channels()
    not_sub_channels = []
    for channel in channel_data:
        if channel[3] == "True":
            user_status = await bot.get_chat_member(channel[0], message.from_user.id)
            if user_status.status not in ["member", "administrator", "creator"]:
                not_sub_channels.append(channel)

    text = ""

    if lang == "uz":
        text += "Botdan foydalanish uchun shu kanallarga obuna bo'lib qo'ying"

    elif lang == "ru":
        text += "Чтобы пользоваться ботом, подпишитесь на эти каналы"

    elif lang == "en":
        text += "To use the bot, please subscribe to these channels"
    await message.answer(
        text,
        reply_markup=not_channels_button(not_sub_channels)
    )





@check_channel_sub_router.callback_query()
async def check_channel_sub_call(call: CallbackQuery, pool: asyncpg.Pool, bot: Bot, lang: str):
    channel_actions = ChannelDataBaseActions(pool)
    channel_data = await channel_actions.get_all_channels()
    not_sub_channels = []
    for channel in channel_data:
        if channel[3] == "True":
            user_status = await bot.get_chat_member(channel[0], call.from_user.id)
            if user_status.status not in ["member", "administrator", "creator"]:
                not_sub_channels.append(channel)

    text = ""

    if lang == "uz":
        text += "Botdan foydalanish uchun shu kanallarga obuna bo'lib qo'ying"

    elif lang == "ru":
        text += "Чтобы пользоваться ботом, подпишитесь на эти каналы"

    elif lang == "en":
        text += "To use the bot, please subscribe to these channels"

    await call.message.answer(
        text,
        reply_markup=not_channels_button(not_sub_channels)
    )
