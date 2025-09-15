from aiogram_dialog import DialogManager
from asyncpg import Connection

from src.app.database.queries.bots import BotActions
from src.app.texts import admin_menu_texts


async def delete_bot_text_getter(dialog_manager: DialogManager, _):
    conn: Connection = dialog_manager.middleware_data["conn"]
    lang: str = dialog_manager.middleware_data["lang"]
    bot_username = dialog_manager.dialog_data.get("bot_username")

    bot_actions = BotActions(conn)

    bot_data = await bot_actions.get_bot(bot_username)

    title = admin_menu_texts["are_you_sure"][lang].format(bot_data[0])

    return {
        "sure": admin_menu_texts["sure"][lang],
        "not_sure": admin_menu_texts["not_sure"][lang],
        "title": title

    }



async def delete_text_getter_pass(dialog_manager: DialogManager, _):
    lang: str = dialog_manager.middleware_data["lang"]

    title = admin_menu_texts["pased_delete_bot"][lang]
    back_kbd_text = admin_menu_texts["back_button"][lang]

    return {"title": title, "back_kbd_text": back_kbd_text}


async def delete_text_getter_failed(dialog_manager: DialogManager, _):
    lang: str = dialog_manager.middleware_data["lang"]

    title = admin_menu_texts["failed_delete_bot"][lang]
    back_kbd_text = admin_menu_texts["back_button"][lang]

    return {"title": title, "back_kbd_text": back_kbd_text}