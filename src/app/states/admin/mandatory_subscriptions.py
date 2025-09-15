from aiogram.fsm.state import StatesGroup, State


class MandatorySubscriptionsSG(StatesGroup):
    menu = State()

class MandatorySubscriptionChannelMenuSG(StatesGroup):
    channel_menu = State()

class MandatorySubscriptionBotMenuSG(StatesGroup):
    bot_menu = State()

class AddChannelSG(StatesGroup):
    get_channel_data = State()
    get_channel_link = State()