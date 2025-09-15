from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from asyncpg import Connection

from src.app.database.queries.channels import ChannelActions


async def on_sure(call: CallbackQuery, _, dialog_manager: DialogManager):
    channel_id = dialog_manager.dialog_data.get("channel_id")
    conn: Connection = dialog_manager.middleware_data["conn"]

    try:
        channel_actions = ChannelActions(conn)
        await channel_actions.delete_channel(channel_id)

        dialog_manager.dialog_data["msg_type"] = "delete_successful"
        return
    except Exception as e:
        print("Error", e)
        dialog_manager.dialog_data["msg_type"] = "error"
        return




