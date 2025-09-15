from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Row, Button, SwitchTo
from aiogram_dialog.widgets.text import Format

from src.app.dialogs.admin_menu.subscription.bots.set_up_bot.delete.getters import (
    delete_bot_text_getter,
    delete_text_getter_pass, delete_text_getter_failed
)
from src.app.dialogs.admin_menu.subscription.bots.set_up_bot.delete.handlers import on_sure
from src.app.states.admin import BotSG, SubscriptionsSG

delete_bot = Window(
    Format("{title}"),
    Row(
        Button(
            Format("{sure}"),
            id="sure",
            on_click=on_sure
        ),
        SwitchTo(
            Format("{no}"),
            id="no",
            state=BotSG.bot_setup_menu
        )
    ),
    state=BotSG.delete_bot,
    getter=delete_bot_text_getter

)


on_sure_bot_pass = Window(
    Format("{title}"),
    Row(
        SwitchTo(
            Format("{back_kbd_text}"),
            id="back_to_subscriptions_menu",
            state=SubscriptionsSG.menu
        )
    ),
    state=BotSG.delete_sure_pass,
    getter=delete_text_getter_pass
)

on_sure_bot_failed = Window(
    Format("{title}"),
    Row(
        SwitchTo(
            Format("{back_kbd_text}"),
            id="back_to_subscriptions_menu",
            state=BotSG.bot_setup_menu
        )
    ),
    state=BotSG.delete_sure_failed,
    getter=delete_text_getter_failed
)


