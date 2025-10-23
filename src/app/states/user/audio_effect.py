from aiogram.fsm.state import StatesGroup, State


class SendAudioSG(StatesGroup):
    send_audio = State()