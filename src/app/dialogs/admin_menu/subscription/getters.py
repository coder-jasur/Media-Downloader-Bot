from aiogram_dialog import DialogManager
from asyncpg import Connection

from src.app.database.queries.bots import BotActions
from src.app.database.queries.channels import ChannelActions
from src.app.texts import admin_menu_texts


async def mandatory_subscriptions_getter(dialog_manager: DialogManager, conn: Connection, lang: str,  **_):
    channel_actions = ChannelActions(conn)
    bot_actions = BotActions(conn)

    try:
        channels_data = await channel_actions.get_all_channels()
        bots_data = await bot_actions.get_all_bots()
        if channels_data or bots_data:
            title = admin_menu_texts[lang]["mandatory_subscriptions_menu"]


        else:
            title = admin_menu_texts["none_menu_subscriptions"][lang]
            dialog_manager.dialog_data["msg_type"] = "not_found"



        return {
            "title": title,
            "msg_type": dialog_manager.dialog_data.get("msg_type", "start_msg"),
            "channels": channels_data if channels_data else [],
            "bots": bots_data if bots_data else [],
            "back_button_text": admin_menu_texts["back_button_text"][lang],
            "add_channel": admin_menu_texts["add_channel"][lang],
            "add_bot": admin_menu_texts["add_bot"][lang],
            "channels_sign": admin_menu_texts["channels"][lang] if channels_data else "",
            "bots_sign": admin_menu_texts["bots"][lang]if bots_data else ""
        }

    except Exception as e:
        print("ERROR", e)
