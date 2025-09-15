from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from src.app.dialogs.language_selection.handlers import on_language_selection
from src.app.states.language_selection import LanguageSelectionSG

language_selection_dialog = Dialog(
    Window(
        Button(Const("O'zingizga qulay tilni tanlang 🇺🇿"), id="uz", on_click=on_language_selection),
        Button(Const("Выбери язык, который тебе нравится 🇷🇺"), id="ru", on_click=on_language_selection),
        Button(Const("Choose the language you like 🇺🇸"), id="en", on_click=on_language_selection),
        state=LanguageSelectionSG.Language_selection
    )
)
