
from aiogram.enums import ContentType
from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Start, Button
from aiogram_dialog.widgets.text import Format, Case

from src.app.dialogs.admin_menu.subscription.channels.add_channel.getters import add_channel_instruction_getter, \
    get_channel_channel_link_instruction_getter
from src.app.dialogs.admin_menu.subscription.channels.add_channel.handlers import take_channel_data, add_channel, \
    on_add_channel_by_defult_link
from src.app.states.admin.mandatory_subscriptions import MandatorySubscriptionsSG, AddChannelSG

add_channel_dialog = Dialog(
    Window(
        Case(
            {
                "start_msg": Format("{title}"),
                "already_exists": Format("{title}"),
                "not_forwarded": Format("{title}"),
                "error": Format("{title}")
            },
            selector="msg_type"
        ),
        MessageInput(func=take_channel_data, content_types=ContentType.ANY),
        Start(Format("{back_button_text}"), id="back", state=MandatorySubscriptionsSG.menu),
        state=AddChannelSG.get_channel_data,
        getter=add_channel_instruction_getter
    ),
    Window(
        Case(
            {
                "start_msg": Format("{title}"),
                "error": Format("{title}"),
                "successful_addition": Format("{title}")
            },
            selector="msg_type"
        ),
        Button(Format("{defult_link}"), id="defult_link", on_click=on_add_channel_by_defult_link),
        MessageInput(func=add_channel, content_types=ContentType.TEXT),
        Start(Format("{back_button_text}"), id="back", state=MandatorySubscriptionsSG.menu),
        state=AddChannelSG.get_channel_link,
        getter=get_channel_channel_link_instruction_getter
    )
)
