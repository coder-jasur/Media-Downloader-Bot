from aiogram.fsm.state import StatesGroup, State


class AddChanenlMessageSG(StatesGroup):
    send_channel_message = State()