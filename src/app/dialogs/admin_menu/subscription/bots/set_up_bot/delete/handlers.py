import asyncpg
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.app.database.queries.bots import BotActions


async def on_sure(call: CallbackQuery, _, dialog_manager: DialogManager):
    bot_username = dialog_manager.dialog_data.get("bot_username")
    pool: asyncpg.Pool = dialog_manager.middleware_data.get("pool")

    try:
        channel_actions = BotActions(pool)
        await channel_actions.delete_bot(bot_username)

        await dialog_manager.switch_to(BotSG.delete_sure_pass)
    except Exception as e:
        print("Error", e)
        await dialog_manager.switch_to(BotSG.delete_sure_failed)