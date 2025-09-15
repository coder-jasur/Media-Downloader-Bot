from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Group, Button, SwitchTo
from aiogram_dialog.widgets.text import Format

from src.app.dialogs.admin_menu.subscription.bots.set_up_bot.getters import bot_data_getter
from src.app.dialogs.admin_menu.subscription.bots.set_up_bot.handlers import on_mandatoriy_subscription_set_up
from src.app.states.admin import BotSG, SubscriptionsSG

bot_setup_menu = Window(
    Format("{title}"),
    Group(
        SwitchTo(
            text=Format("{delete_bot_kbd_text}"),
            id="delite_bot",
            state=BotSG.delete_bot
        ),
        Button(
            text=Format("{setup_mandatory_subscription_kbd_text}"),
            id="setup_mandatory_subscription",
            on_click=on_mandatoriy_subscription_set_up
        ),
        SwitchTo(
            text=Format("{back_to_subscriptions_menu_kbd_text}"),
            id="back_to_subscriptions_menu",
            state=SubscriptionsSG.menu
        ),
        width=2
    ),
    state=BotSG.bot_setup_menu,
    getter=bot_data_getter
)
