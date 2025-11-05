import asyncpg
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.app.database.queries.channels import ChannelDataBaseActions
from src.app.database.queries.users import UserDataBaseActions
from src.app.keyboards.inline import not_channels_button
from src.app.states.check_channel_sub import ChooseLanguageSG
from src.app.utils.i18n import get_translator

check_sub_router = Router()

@check_sub_router.callback_query(F.data == "check_sub")
async def check_channel_sub(
    call: CallbackQuery,
    dialog_manager: DialogManager,
    pool: asyncpg.Pool,
    bot: Bot,
    lang: str,
):
    _ = get_translator(lang).gettext
    channel_actions = ChannelDataBaseActions(pool)
    user_actions = UserDataBaseActions(pool)
    user_data = await user_actions.get_user(dialog_manager.event.from_user.id)
    channel_data = await channel_actions.get_all_channels()
    not_sub_channels = []

    for channel in channel_data:
        if channel[3] == "True":
            user_status = await bot.get_chat_member(channel[0], dialog_manager.event.from_user.id)
            if user_status.status not in ["member", "administrator", "creator"]:
                not_sub_channels.append(channel)

    text = ""

    if lang == "uz":
        text += "Botdan foydalanish uchun shu kanallarga obuna bo'lib qo'ying"

    elif lang == "ru":
        text += "Чтобы пользоваться ботом, подпишитесь на эти каналы"

    elif lang == "en":
        text += "To use the bot, please subscribe to these channels"

    if not not_sub_channels:
        if not user_data[3]:
            await dialog_manager.start(ChooseLanguageSG.choose_language)
        else:
            await call.message.answer(_("Start text"))
    elif not_sub_channels:
        await dialog_manager.event.message.answer(
            text + ".",
            reply_markup=not_channels_button(not_sub_channels)
        )
    else:
        try:
            await dialog_manager.event.message.edit_text(
                text,
                reply_markup=not_channels_button(channel_data),
            )

        except Exception as e:
            print(e)
            await dialog_manager.event.message.edit_text(
                text + ".",
                reply_markup=not_channels_button(channel_data),
            )
