from aiogram.fsm.state import StatesGroup, State


class AddReferalSG(StatesGroup):
    get_referal_name = State()