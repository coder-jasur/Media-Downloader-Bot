from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile
from aiogram_dialog import DialogManager, StartMode, ShowMode

from src.app.keyboards.callback_data import SearchMusicInVideoCD
from src.app.states.admin.admin import AdminSG

admin_commands_router = Router()


@admin_commands_router.message(Command("admin_menu"))
async def main_admin_menu(_, dialog_manager: DialogManager):
    await dialog_manager.start(AdminSG.menu, mode=StartMode.RESET_STACK)



