from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from asyncpg import Connection

from src.app.database.queries.channels import ChannelActions
from src.app.states.admin.mandatory_subscriptions import AddChannelSG


async def take_channel_data(message: Message, _, dialog_manager: DialogManager):
    conn: Connection = dialog_manager.middleware_data.get("conn")
    channel_actions = ChannelActions(conn)
    try:
        if not message.forward_from_chat:
            dialog_manager.dialog_data["msg_type"] = "not_forwarded"
            await dialog_manager.switch_to(AddChannelSG.get_channel_data)
            return

        channel_data = await channel_actions.get_channel(message.forward_from_chat.id)
        if channel_data:
            dialog_manager.dialog_data["msg_type"] = "already_exists"
            await dialog_manager.switch_to(AddChannelSG.get_channel_data)
            return


        channel_data = {
            "channel_id": message.forward_from_chat.id,
            "channel_username": message.forward_from_chat.username or message.forward_from_chat.full_name,
            "channel_name": message.forward_from_chat.full_name
        }
        dialog_manager.dialog_data["channel_data"] = channel_data
        dialog_manager.dialog_data.pop("msg_type", None)
        await dialog_manager.next()
        return

    except Exception as e:
        print("ERROR", e)
        dialog_manager.dialog_data["msg_type"] = "error"
        await dialog_manager.switch_to(AddChannelSG.get_channel_data)
        return

async def add_channel(_, message_input: MessageInput, dialog_manager: DialogManager):
    conn: Connection = dialog_manager.middleware_data.get("conn")
    channel_actions = ChannelActions(conn)

    try:
        channel_data = dialog_manager.dialog_data.get("channel_data")
        await channel_actions.add_channel(
            channel_data["channel_id"],
            channel_data["channel_name"],
            channel_data["channel_username"],
            message_input.widget_id
        )
        dialog_manager.dialog_data["msg_type"] = "successful_addition"
        return

    except Exception as e:
        print("ERROR", e)
        dialog_manager.dialog_data["msg_type"] = "error"
        await dialog_manager.switch_to(AddChannelSG.get_channel_link)

async def on_add_channel_by_defult_link(_, __, dialog_manager: DialogManager):
    conn: Connection = dialog_manager.middleware_data.get("conn")
    channel_actions = ChannelActions(conn)
    print()

    try:
        channel_data = dialog_manager.dialog_data.get("channel_data")
        await channel_actions.add_channel(
            channel_data["channel_id"],
            channel_data["channel_name"],
            channel_data["channel_username"],
            f"https://t.me/{channel_data["channel_username"]}"
        )
        dialog_manager.dialog_data["msg_type"] = "successful_addition"
        return

    except Exception as e:
        print("ERROR", e)
        dialog_manager.dialog_data["msg_type"] = "error"
        await dialog_manager.switch_to(AddChannelSG.get_channel_link)