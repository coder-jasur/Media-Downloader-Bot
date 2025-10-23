import asyncpg
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from asyncpg import Connection

from src.app.database.queries.users import UserActions


async def on_language_selection(_, button: Button, dialog_manager: DialogManager):
    pool: asyncpg.Pool = dialog_manager.middleware_data.get("pool")
    user_actions = UserActions(pool)

    try:
        user = dialog_manager.event.from_user
        user_data = await user_actions.get_user(user.id)

        if not user_data:
            await user_actions.add_user(user.id, user.username or user.full_name, button.widget_id)

        await user_actions.update_user_lang(button.widget_id, user.id)

    except Exception as e:
        print("ERROR", e)

