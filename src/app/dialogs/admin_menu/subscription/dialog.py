from operator import itemgetter

from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Button, Start, Select, Row
from aiogram_dialog.widgets.text import Format, Case

from src.app.dialogs.admin_menu.subscription.getters import mandatory_subscriptions_getter
from src.app.dialogs.admin_menu.subscription.handlers import on_click_set_up_channel
from src.app.states.admin.admin import AdminSG
from src.app.states.admin.mandatory_subscriptions import MandatorySubscriptionsSG, AddChannelSG

mandatory_subscriptions_dialog = Dialog(
    Window(
        Case(
            {
                "start_msg": Format("{title}"),
                "not_found": Format("{title}")
            },
            selector="msg_type"
        ),
        Button(Format("{channels_sign}"), id="channels"),
        Select(
            Format("{item[1]}"),
            id="mandatory_subscriptions",
            item_id_getter=itemgetter(0),
            items="channels",
            on_click=on_click_set_up_channel
        ),
        Button(Format("{bots_sign}"), id="bots"),
        Select(
            Format("{item[1]}"),
            id="mandatory_subscriptions",
            item_id_getter=itemgetter(0),
            items="bots",
            on_click=on_click_set_up_channel
        ),
        Row(
            Start(Format("{add_channel}"), id="add_channel", state=AddChannelSG.get_channel_data),
            Start(Format("{add_bot}"), id="add_bot", state=...)
        ),
        Start(Format("{back_button_text}"), id="back", state=AdminSG.menu),
        state=MandatorySubscriptionsSG.menu,
        getter=mandatory_subscriptions_getter
    )
)
