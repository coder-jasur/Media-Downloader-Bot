import asyncpg
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.app.database.queries.channels import ChannelDataBaseActions
from src.app.handlers.admin.menu.helpers import _show_subscriptions_menu_message
from src.app.handlers.admin.menu.menu import _handle_subscriptions_menu
from src.app.keyboards.callback_data import ChannelCD, AddMandatorySubscriptionCD
from src.app.keyboards.inline import (
    modified_channel_menu,
    delite_channel_menu,
    back_to_subscription_menu,
    add_chanel_url_defult
)
from src.app.states.admin.add_channel import AddChannelSG
from src.app.utils.enums.actions import ChannelActions, AddMandatorySubscriptionActions
from src.app.utils.i18n import get_translator

channels_router = Router(name="channels_admin")


@channels_router.callback_query(ChannelCD.filter())
async def handle_channel_actions(
        call: CallbackQuery,
        callback_data: ChannelCD,
        pool: asyncpg.Pool,
        lang: str,
):
    """Kanal action handler"""
    channel_actions = ChannelDataBaseActions(pool)
    _ = get_translator(lang).gettext

    # Action handlers mapping
    action_handlers = {
        ChannelActions.DELETE_IN_MANDATORY_SUB: _toggle_channel_status,
        ChannelActions.ADD_IN_MANDATORY_SUB: _toggle_channel_status,
        ChannelActions.DELETE_CHANNEL: _show_delete_confirmation,
        ChannelActions.SURE_DELETE: _delete_channel,
        ChannelActions.NOT_SURE_DELETE: lambda: None,  # Do nothing
    }

    handler = action_handlers.get(callback_data.action)
    if handler:
        result = await handler(call, callback_data, pool, lang)
        if result == "return":  # Agar return signal bo'lsa
            return

    # Kanal menyusini ko'rsatish
    await _show_channel_menu(call, callback_data.id, pool, lang)


async def _toggle_channel_status(call, callback_data, pool, lang):
    """Kanal statusini o'zgartirish"""
    channel_actions = ChannelDataBaseActions(pool)
    channel = await channel_actions.get_channel(callback_data.id)

    new_status = "False" if channel[3] == "True" else "True"
    await channel_actions.update_channel_status(new_status, callback_data.id)


async def _show_delete_confirmation(call, callback_data, pool, lang):
    """O'chirish tasdiqini so'rash"""
    _ = get_translator(lang).gettext
    await call.message.edit_text(
        _("Delete channel choose"),
        reply_markup=delite_channel_menu(callback_data.id, lang)
    )
    return "return"


async def _delete_channel(call, callback_data, pool, lang):
    """Kanalni o'chirish"""
    _ = get_translator(lang).gettext
    await ChannelDataBaseActions(pool).delete_channel(callback_data.id)
    await call.answer(_("Passed Delete"))

    await _handle_subscriptions_menu(call, pool, lang)
    return "return"


async def _show_channel_menu(call, channel_id, pool, lang):
    """Kanal sozlamalar menyusini ko'rsatish"""
    _ = get_translator(lang).gettext
    channel = await ChannelDataBaseActions(pool).get_channel(channel_id)

    await call.message.edit_text(
        _("Channel set up menu title").format(
            channel[0], channel[1], channel[2], channel[3], channel[4]
        ),
        reply_markup=modified_channel_menu(
            channel_id,
            channel[3] == "True",
            lang
        )
    )


@channels_router.callback_query(
    AddMandatorySubscriptionCD.filter(
        F.actions == AddMandatorySubscriptionActions.ADD_CHANNEL
    )
)
async def start_add_channel(call: CallbackQuery, state: FSMContext, lang: str):
    """Kanal qo'shish jarayonini boshlash"""
    _ = get_translator(lang).gettext
    await state.set_state(AddChannelSG.get_channle_id)
    await call.message.answer(
        _("Send post for channel or group"),
        reply_markup=back_to_subscription_menu(lang)
    )


@channels_router.message(AddChannelSG.get_channle_id)
async def process_channel_id(message: Message, state: FSMContext, lang: str):
    """Kanal ID qabul qilish"""
    _ = get_translator(lang).gettext

    if not message.forward_from_chat:
        await message.answer(
            _("Forward only from chat"),
            reply_markup=back_to_subscription_menu(lang)
        )
        return

    await state.update_data(channel_id=message.forward_from_chat.id)
    await state.set_state(AddChannelSG.get_channel_url)
    await message.answer(_("Send url"), reply_markup=add_chanel_url_defult(lang))


@channels_router.message(AddChannelSG.get_channel_url)
async def process_channel_url(
        message: Message,
        state: FSMContext,
        pool: asyncpg.Pool,
        bot: Bot,
        lang: str
):
    """Kanal URL qabul qilish"""
    _ = get_translator(lang).gettext
    data = await state.get_data()

    channels_actions = ChannelDataBaseActions(pool)

    # Kanal mavjudligini tekshirish
    if await channels_actions.get_channel(data.get("channel_id")):
        await message.answer(
            _("Channel already exists"),
            reply_markup=back_to_subscription_menu(lang)
        )
        return

    # Kanal ma'lumotlarini olish
    channel_info = await bot.get_chat(data["channel_id"])

    # Kanalni qo'shish
    await channels_actions.add_channel(
        channel_info.id,
        channel_info.full_name,
        channel_info.username or None,
        message.text
    )

    await state.clear()
    await message.answer(_("Channel successfully added!"))

    # Menyu ko'rsatish
    await _show_subscriptions_menu_message(message, pool, lang)


@channels_router.callback_query(
    AddMandatorySubscriptionCD.filter(
        F.actions == AddMandatorySubscriptionActions.ADD_CHANNEL_URL_DEFULT
    )
)
async def add_channel_with_default_url(
        call: CallbackQuery,
        state: FSMContext,
        pool: asyncpg.Pool,
        bot: Bot,
        lang: str
):
    """Default URL bilan kanal qo'shish"""
    _ = get_translator(lang).gettext
    data = await state.get_data()

    channels_actions = ChannelDataBaseActions(pool)

    if await channels_actions.get_channel(data.get("channel_id")):
        await call.message.edit_text(
            _("Channel already exists"),
            reply_markup=back_to_subscription_menu(lang)
        )
        return

    channel_info = await bot.get_chat(data["channel_id"])
    await channels_actions.add_channel(
        channel_info.id,
        channel_info.full_name,
        channel_info.username or None,
        channel_info.invite_link
    )

    await state.clear()

    await _handle_subscriptions_menu(call, pool, lang)