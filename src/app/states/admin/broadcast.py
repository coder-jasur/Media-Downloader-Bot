from aiogram.fsm.state import StatesGroup, State


class BroadcastingManagerSG(StatesGroup):
    get_message = State()
    confirm_broadcasting = State()