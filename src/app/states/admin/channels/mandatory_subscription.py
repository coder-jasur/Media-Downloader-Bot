from aiogram.fsm.state import StatesGroup, State


class MandatorySubscription(StatesGroup):
    set_up_subscription = State()