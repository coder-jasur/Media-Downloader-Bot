from aiogram import Dispatcher, Router

from src.app.dialogs.admin_menu import register_admin_dialogs
from src.app.dialogs.language_selection.dialog import language_selection_dialog


def register_all_dialogs(router: Router):
    register_admin_dialogs(router)
    router.include_router(language_selection_dialog)
