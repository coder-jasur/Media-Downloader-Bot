from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Button, Row, Start
from aiogram_dialog.widgets.text import Format, Case

from src.app.dialogs.admin_menu.subscription.channels.set_up_channel.delete.getters import get_texts_delete_channel_dialog
from src.app.dialogs.admin_menu.subscription.channels.set_up_channel.delete.handlers import on_sure
from src.app.states.admin.channels.delete_channel import DeleteChanenlSG
from src.app.states.admin.mandatory_subscriptions import MandatorySubscriptionChannelMenuSG

delete_channel_dialog = Dialog(
    Window(
        Case(
            {
                "start_msg": Format("{title}"),
                "delete_successful": Format("{title}"),
                "error": Format("{title}")
            },
            selector="msg_type"
        ),
        Row(
            Button(
                Format("{sure}"),
                id="sure",
                on_click=on_sure
            ),
            Start(
                Format("{no}"),
                id="no",
                state=MandatorySubscriptionChannelMenuSG.channel_menu
            )
        ),
        state=DeleteChanenlSG.delete_channel,
        getter=get_texts_delete_channel_dialog

    )
)
