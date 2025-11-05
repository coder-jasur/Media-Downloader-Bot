from aiogram import Dispatcher, Router

from src.app.dialogs.language_selection.dialog import language_selection_dialog


def register_all_dialogs(router: Router):
    router.include_router(language_selection_dialog)
