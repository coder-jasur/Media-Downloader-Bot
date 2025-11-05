import asyncpg
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram_dialog import DialogManager, StartMode, ShowMode

from src.app.handlers.admin.menu.menu import _handle_subscriptions_menu
from src.app.keyboards.inline import admin_main_menu
from src.app.utils.i18n import get_translator

admin_commands_router = Router()


@admin_commands_router.message(Command("admin_menu"))
async def main_admin_menu(message: Message, lang: str):
    _ = get_translator(lang).gettext
    await message.answer(_("Admin main menu title"), reply_markup=admin_main_menu(lang))



@admin_commands_router.callback_query(F.data.in_(["back_to_menu", "back_to_subscriptions_menu"]))
async def back_to_subscriptions(call: CallbackQuery, pool: asyncpg.Pool, lang: str):
    """Subscription menyuga qaytish"""
    await _handle_subscriptions_menu(call, pool, lang)




