from aiogram_dialog import DialogManager
from asyncpg import Connection

from src.app.database.queries.bots import BotActions
from src.app.texts import admin_menu_texts


async def bot_data_getter(dialog_manager: DialogManager, _):
    bot_username = dialog_manager.start_data.get("bot_username")
    conn: Connection = dialog_manager.middleware_data["conn"]
    lang: str = dialog_manager.middleware_data["lang"]
    bot_actions = BotActions(conn)

    bot_data = await bot_actions.get_bot(bot_username)
    bot_status = admin_menu_texts["mandatoriy_subscription"][bot_data[2]][lang]


    title = admin_menu_texts["bot_info_text"][lang].format(
        bot_data[0],
        bot_data[1],
        bot_status,
        bot_data[1],

    )

    if bot_data[2] == "True":
        msb = admin_menu_texts["delete_from_mandatory"][lang]
    else:
        msb = admin_menu_texts["add_to_mandatory"][lang]



    return {
        "title": title,
        "setup_mandatory_subscription_kbd_text": msb,
        "delete_bot_button_kbd_text": admin_menu_texts["delete_bot"][lang],
        "back_to_subscriptions_menu_kbd_text": admin_menu_texts["back_button"][lang],
    }