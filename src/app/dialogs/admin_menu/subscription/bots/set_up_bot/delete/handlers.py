from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from asyncpg import Connection

from src.app.database.queries.bots import BotActions
from src.app.states.admin import BotSG


async def on_sure(call: CallbackQuery, _, dialog_manager: DialogManager):
    bot_username = dialog_manager.dialog_data.get("bot_username")
    conn: Connection = dialog_manager.middleware_data["conn"]

    try:
        channel_actions = BotActions(conn)
        await channel_actions.delete_bot(bot_username)

        await dialog_manager.switch_to(BotSG.delete_sure_pass)
    except Exception as e:
        print("Error", e)
        await dialog_manager.switch_to(BotSG.delete_sure_failed)