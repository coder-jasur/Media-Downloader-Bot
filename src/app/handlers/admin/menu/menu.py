import asyncpg
from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.app.database.queries.channels import ChannelDataBaseActions
from src.app.database.queries.bots import BotDataBaseActions
from src.app.database.queries.referals import ReferalDataBaseActions
from src.app.database.queries.users import UserDataBaseActions
from src.app.keyboards.callback_data import AdminMainMenuCD
from src.app.keyboards.inline import (
    admin_main_menu,
    create_mandatory_subs_keyboard,
    referals_menu_kbd,
    back_to_channel_menu
)
from src.app.utils.enums.actions import AdminMenuActions
from src.app.utils.i18n import get_translator

admin_menu_router = Router(name="admin_menu")


@admin_menu_router.callback_query(AdminMainMenuCD.filter())
async def handle_admin_menu(
        call: CallbackQuery,
        callback_data: AdminMainMenuCD,
        pool: asyncpg.Pool,
        lang: str
):
    """Admin menyu navigation handler"""
    _ = get_translator(lang).gettext

    handlers = {
        AdminMenuActions.MANDATORY_SUBSCRIPTIONS_MENU: _handle_subscriptions_menu,
        AdminMenuActions.REFERALS_MENU: _handle_referrals_menu,
        AdminMenuActions.STATISTICS_MENU: _handle_statistics_menu,
    }

    handler = handlers.get(callback_data.actions)
    if handler:
        await handler(call, pool, lang)
    else:
        await call.answer(_("Coming soon..."), show_alert=True)


async def _handle_subscriptions_menu(call: CallbackQuery, pool: asyncpg.Pool, lang: str):
    """Majburiy obuna menyusi"""
    _ = get_translator(lang).gettext

    channels_data = await ChannelDataBaseActions(pool).get_all_channels()
    bots_data = await BotDataBaseActions(pool).get_all_bots()

    text = (
        _("Mandatory subscriptions menu title")
        if channels_data or bots_data
        else _("Empty mandatory subscriptions menu title")
    )

    await call.message.edit_text(
        text,
        reply_markup=create_mandatory_subs_keyboard(channels_data, bots_data, lang)
    )


async def _handle_referrals_menu(call: CallbackQuery, pool: asyncpg.Pool, lang: str):
    """Referral menyusi"""
    _ = get_translator(lang).gettext

    referrals_data = await ReferalDataBaseActions(pool).get_all_referals()

    text = (
        _("Referals menu title")
        if referrals_data
        else _("Empty referals menu title")
    )

    await call.message.edit_text(
        text,
        reply_markup=referals_menu_kbd(referrals_data, lang)
    )


async def _handle_statistics_menu(call: CallbackQuery, pool: asyncpg.Pool, lang: str):
    """Statistika menyusi"""
    stats = await UserDataBaseActions(pool).get_user_statistics()

    _ = get_translator(lang).gettext
    text = _("users statistics format text").format(
        stats['today'],
        stats['week'],
        stats['month'],
        stats['year'],
        stats['total']
    )

    await call.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=back_to_channel_menu(lang)
    )


@admin_menu_router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu_handler(call: CallbackQuery, lang: str):
    """Admin menyuga qaytish"""
    _ = get_translator(lang).gettext
    await call.message.edit_text(
        _("Admin main menu title"),
        reply_markup=admin_main_menu(lang)
    )
