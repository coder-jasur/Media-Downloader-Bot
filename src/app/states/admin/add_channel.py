from aiogram.fsm.state import StatesGroup, State


class AddChannelSG(StatesGroup):
    get_channle_id = State()
    get_channel_url = State()