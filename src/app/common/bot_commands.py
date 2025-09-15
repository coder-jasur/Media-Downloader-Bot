from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

from src.app.core.config import Settings


async def bot_commands(bot: Bot, settings: Settings):
    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Restart"),
            BotCommand(command="language", description="Choose a language"),
            BotCommand(command="about", description="About")
        ],
    )

    for admin_id in settings.admins_ids:
        scoupe = BotCommandScopeChat(chat_id=int(admin_id))

        await bot.set_my_commands(
            commands=[
                BotCommand(command="start", description="Restart"),
                BotCommand(command="language", description="Choose a language"),
                BotCommand(command="about", description="About"),
                BotCommand(command="admin_menu", description="Admin main_menu")
            ],
            scope=scoupe
        )