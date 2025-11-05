from aiogram.fsm.state import StatesGroup, State


class AddBotSG(StatesGroup):
    get_bot_username = State()
    get_bot_name = State()
    get_bot_url = State()