from aiogram.fsm.state import StatesGroup, State


class ChooseLanguageSG(StatesGroup):
    choose_language = State()


class ChooseTranslateLanguagesSG(StatesGroup):
    choose_language = State()