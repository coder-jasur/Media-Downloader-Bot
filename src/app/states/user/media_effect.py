from aiogram.fsm.state import StatesGroup, State


class SendMediaSG(StatesGroup):
    send_media = State()