from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Group, Button, SwitchTo, Start
from aiogram_dialog.widgets.text import Format

from src.app.dialogs.admin_menu.subscription.channels.set_up_channel.getters import get_text_channel_set_up_menu
from src.app.dialogs.admin_menu.subscription.channels.set_up_channel.handlers import (
    on_click_mandatory_subscription,
    on_delete_channel_message
)
from src.app.states.admin.channels.delete_channel import DeleteChanenlSG
from src.app.states.admin.mandatory_subscriptions import MandatorySubscriptionChannelMenuSG, MandatorySubscriptionsSG

channel_set_up_menu = Dialog(
    Window(
        Format("{title}"),
        Group(
            SwitchTo(
                text=Format("{delite_channel_button_kbd_text}"),
                id="delite_channel",
                state=DeleteChanenlSG.delete_channel
            ),
            Button(
                Format("{setup_mandatory_subscription_kbd_text}"),
                id="setup_mandatory_subscription",
                on_click=on_click_mandatory_subscription
            ),
            Button(
                Format("{add_channel_message_kbd_text}"),
                id="add_channel_message",
                on_click=...
            ),
            Button(
                Format("{delite_channel_message_kbd_text}"),
                id="delite_channel_message",
                on_click=on_delete_channel_message
            ),
            Start(
                Format("{back_to_subscriptions_menu_kbd_text}"),
                id="back_to_subscriptions_menu",
                state=MandatorySubscriptionsSG.menu
            ),
            width=1
        ),
        state=MandatorySubscriptionChannelMenuSG.channel_menu,
        getter=get_text_channel_set_up_menu
    )
)
