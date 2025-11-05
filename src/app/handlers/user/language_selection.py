from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from src.app.dialogs import language_selection_dialog
from src.app.states.language_selection import LanguageSelectionSG

language_selection_router = Router()

@language_selection_router.message(Command("lang"))
async def language_selection(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(LanguageSelectionSG.Language_selection)