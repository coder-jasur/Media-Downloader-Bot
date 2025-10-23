import asyncpg
from aiogram_dialog import DialogManager
from asyncpg import Connection

from src.app.database.queries.channels import ChannelActions
from src.app.texts import admin_menu_texts


async def get_text_channel_set_up_menu(dialog_manager: DialogManager, pool: asyncpg.Pool, lang: str, **_):
    channel_id = dialog_manager.start_data
    dialog_manager.dialog_data["channel_id"] = channel_id
    channel_actions = ChannelActions(pool)
    channel_data = await channel_actions.get_channel(int(channel_id))
    channel_status = admin_menu_texts["mandatoriy_subscription"][channel_data[3]][lang]


    channel_info_text = admin_menu_texts["channel_info_text"][lang].format(
        channel_data[0],
        channel_data[1],
        channel_data[2],
        channel_status,
        channel_data[2]
    )

    if channel_data[3] == "True":
        msb = admin_menu_texts["delete_from_mandatory"][lang]
    else:
        msb = admin_menu_texts["add_to_mandatory"][lang]


    return {
        "title": channel_info_text,
        "setup_mandatory_subscription_kbd_text": msb,
        "delite_channel_button_kbd_text": admin_menu_texts["delete_channel"][lang],
        "back_to_subscriptions_menu_kbd_text": admin_menu_texts["back_button"][lang],
        "add_channel_message_kbd_text": admin_menu_texts["add_channel_message_button"][lang],
        "delite_channel_message_kbd_text":  "🗑" if channel_data[4] else ""
    }
