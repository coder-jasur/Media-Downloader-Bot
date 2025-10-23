from aiogram_dialog import DialogManager

from src.app.texts import admin_menu_texts


async def add_channel_instruction_getter(dialog_manager: DialogManager, lang: str, **_):
    try:

        title = admin_menu_texts["add_channel_title"][lang]

        if dialog_manager.dialog_data.get("msg_type") == "not_forwarded":
            title = admin_menu_texts["not_forwarded"][lang]

        if dialog_manager.dialog_data.get("msg_type") == "already_exists":
            title = admin_menu_texts["already_exists"][lang]

        if dialog_manager.dialog_data.get("msg_type") == "error":
            title = admin_menu_texts["failed_add_channel"][lang]


        return {
            "title": title,
            "back_button_text": admin_menu_texts["back_button_text"][lang],
            "msg_type": dialog_manager.dialog_data.get("msg_type", "start_msg")
        }

    except Exception as e:
        print("ERROR", e)


async def get_channel_channel_link_instruction_getter(dialog_manager: DialogManager, lang: str, **_):
    try:

        title = admin_menu_texts["get_channel_link"][lang]

        if dialog_manager.dialog_data.get("msg_type") == "error":
            title = admin_menu_texts["failed_add_channel"][lang]

        if dialog_manager.dialog_data.get("msg_type") == "successful_addition":
            title = admin_menu_texts["passed_add_channel"][lang]


        return {
            "title": title,
            "back_button_text": admin_menu_texts["back_button_text"][lang],
            "msg_type": dialog_manager.dialog_data.get("msg_type", "start_msg"),
            "defult_link": admin_menu_texts["defult_link"][lang] if title != admin_menu_texts["passed_add_channel"][lang] else ""
        }

    except Exception as e:
        print("ERROR", e)
