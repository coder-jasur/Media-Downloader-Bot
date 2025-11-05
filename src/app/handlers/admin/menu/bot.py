import asyncpg
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.app.database.queries.bots import BotDataBaseActions
from src.app.handlers.admin.menu.helpers import _show_subscriptions_menu_message
from src.app.handlers.admin.menu.menu import _handle_subscriptions_menu
from src.app.keyboards.callback_data import BotCD, AddMandatorySubscriptionCD
from src.app.keyboards.inline import (
    modified_bot_menu,
    delite_bot_menu,
    back_to_subscription_menu,
    add_bot_url_defult
)
from src.app.states.admin.add_bot import AddBotSG
from src.app.utils.enums.actions import BotActions, AddMandatorySubscriptionActions
from src.app.utils.i18n import get_translator

bots_router = Router(name="bots_admin")


@bots_router.callback_query(BotCD.filter())
async def handle_bot_actions(
        call: CallbackQuery,
        callback_data: BotCD,
        pool: asyncpg.Pool,
        lang: str,
):
    """Bot action handler"""
    bot_actions = BotDataBaseActions(pool)
    _ = get_translator(lang).gettext

    # Action handlers
    if callback_data.action in [BotActions.DELETE_IN_MANDATORY_SUB, BotActions.ADD_IN_MANDATORY_SUB]:
        await _toggle_bot_status(callback_data.username, pool)

    elif callback_data.action == BotActions.DELETE_BOT:
        await call.message.edit_text(
            _("Delete bot choose").format(callback_data.username),
            reply_markup=delite_bot_menu(callback_data.username, lang)
        )
        return

    elif callback_data.action == BotActions.SURE_DELETE:
        await bot_actions.delete_bot(callback_data.username)
        await call.answer(_("Passed Delete"))

        from src.app.handlers.admin.menu import _handle_subscriptions_menu
        await _handle_subscriptions_menu(call, pool, lang)
        return

    elif callback_data.action == BotActions.NOT_SURE_DELETE:
        pass  # Do nothing

    # Bot menyusini ko'rsatish
    await _show_bot_menu(call, callback_data.username, pool, lang)


async def _toggle_bot_status(username: str, pool: asyncpg.Pool):
    """Bot statusini o'zgartirish"""
    bot_actions = BotDataBaseActions(pool)
    bot_data = await bot_actions.get_bot(username)

    new_status = "False" if bot_data[2] == "True" else "True"
    await bot_actions.update_bot_status(new_status, username)


async def _show_bot_menu(call, username, pool, lang):
    """Bot sozlamalar menyusini ko'rsatish"""
    _ = get_translator(lang).gettext
    bot_data = await BotDataBaseActions(pool).get_bot(username)

    await call.message.edit_text(
        _("Bot set up menu title").format(
            bot_data[0], bot_data[1], bot_data[2], bot_data[3]
        ),
        reply_markup=modified_bot_menu(
            bot_data[2] == "True",
            username,
            lang
        )
    )


@bots_router.callback_query(
    AddMandatorySubscriptionCD.filter(
        F.actions == AddMandatorySubscriptionActions.ADD_BOT
    )
)
async def start_add_bot(call: CallbackQuery, state: FSMContext, lang: str):
    """Bot qo'shish jarayonini boshlash"""
    _ = get_translator(lang).gettext
    await state.set_state(AddBotSG.get_bot_username)
    await call.message.answer(
        _("Send bot username"),
        reply_markup=back_to_subscription_menu(lang)
    )


@bots_router.message(AddBotSG.get_bot_username)
async def process_bot_username(message: Message, state: FSMContext, lang: str):
    """Bot username qabul qilish"""
    _ = get_translator(lang).gettext

    if not (message.text and message.text.startswith("@")):
        await message.answer(
            _("Send bot username in format: @username"),
            reply_markup=back_to_subscription_menu(lang)
        )
        return

    await state.update_data(bot_username=message.text)
    await state.set_state(AddBotSG.get_bot_name)
    await message.answer(_("Send name"), reply_markup=back_to_subscription_menu(lang))


@bots_router.message(AddBotSG.get_bot_name)
async def process_bot_name(message: Message, state: FSMContext, lang: str):
    """Bot nomi qabul qilish"""
    _ = get_translator(lang).gettext

    if not message.text:
        await message.answer(
            _("Forward only text"),
            reply_markup=back_to_subscription_menu(lang)
        )
        return

    await state.update_data(bot_name=message.text)
    await state.set_state(AddBotSG.get_bot_url)
    await message.answer(_("Send url"), reply_markup=add_bot_url_defult(lang))


@bots_router.message(AddBotSG.get_bot_url)
async def process_bot_url(
        message: Message,
        state: FSMContext,
        lang: str,
        pool: asyncpg.Pool
):
    """Bot URL qabul qilish"""
    _ = get_translator(lang).gettext
    data = await state.get_data()

    bots_actions = BotDataBaseActions(pool)

    # Bot mavjudligini tekshirish
    if await bots_actions.get_bot(data.get("bot_username")):
        await message.answer(
            _("Bot already exists"),
            reply_markup=back_to_subscription_menu(lang)
        )
        return

    # Botni qo'shish
    await bots_actions.add_bot(
        data["bot_name"],
        data["bot_username"],
        message.text
    )

    await state.clear()
    await message.answer(
        _("Bot successfully added!"),
        reply_markup=back_to_subscription_menu(lang)
    )

    await _show_subscriptions_menu_message(message, pool, lang)



@bots_router.callback_query(
    AddMandatorySubscriptionCD.filter(
        F.actions == AddMandatorySubscriptionActions.ADD_BOT_URL_DEFULT
    )
)
async def add_bot_with_default_url(
        call: CallbackQuery,
        state: FSMContext,
        pool: asyncpg.Pool,
        lang: str
):
    """Default URL bilan bot qo'shish"""
    _ = get_translator(lang).gettext
    data = await state.get_data()

    bots_actions = BotDataBaseActions(pool)

    if await bots_actions.get_bot(data.get("bot_username")):
        await call.message.answer(
            _("Bot already exists"),
            reply_markup=back_to_subscription_menu(lang)
        )
        return

    await bots_actions.add_bot(
        data["bot_name"],
        data["bot_username"],
        f"https://t.me/{data['bot_username'].lstrip('@')}"
    )

    await state.clear()

    await _handle_subscriptions_menu(call, pool, lang)
