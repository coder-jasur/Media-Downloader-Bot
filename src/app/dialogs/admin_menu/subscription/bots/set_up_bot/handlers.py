from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from asyncpg import Connection

from src.app.database.queries.bots import BotActions
from src.app.dialogs.admin_menu.subscription.bots.set_up_bot.getters import bot_data_getter
from src.app.texts import admin_menu_texts


async def on_mandatoriy_subscription_set_up(call: CallbackQuery, _, dialog_manager: DialogManager):
    conn: Connection = dialog_manager.middleware_data["conn"]
    lang: str = dialog_manager.middleware_data["lang"]
    bot_username = dialog_manager.dialog_data.get("bot_username")
    channel_actions = BotActions(conn)
    channel_data = await channel_actions.get_bot(bot_username)
    if channel_data[3] == "True":
        await channel_actions.update_bot_status("False", bot_username)
    elif channel_data[3] == "False":
        await channel_actions.update_bot_status("True", bot_username)
    else:
        await call.answer(admin_menu_texts["error_mandatoriy_subscription"][lang])

    data = await bot_data_getter(dialog_manager, _)

    await dialog_manager.update(data)
