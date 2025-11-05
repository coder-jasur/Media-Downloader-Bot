from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat

from src.app.core.config import Settings


# async def bot_commands(bot: Bot, settings: Settings):
#     await bot.set_my_commands(
#         commands=[
#             BotCommand(command="start", description="Restart"),
#             BotCommand(command="top", description="Top Popular Songs"),
#             BotCommand(command="lang", description="Choose a language"),
#             BotCommand(command="media_effect", description="Media effect"),
#             BotCommand(command="about", description="About"),
#
#         ],
#     )
#
#     for admin_id in settings.admins_ids:
#         scoupe = BotCommandScopeChat(chat_id=int(admin_id))
#
#         await bot.set_my_commands(
#             commands=[
#                 BotCommand(command="start", description="Restart"),
#                 BotCommand(command="top", description="Top Popular Songs"),
#                 BotCommand(command="lang", description="Choose a language"),
#                 BotCommand(command="media_effect", description="Media effect"),
#                 BotCommand(command="about", description="About"),
#                 BotCommand(command="admin_menu", description="Admin main menu")
#             ],
#             scope=scoupe
#         )


async def bot_commands(bot: Bot, settings: Settings):

    user_commands = [
        BotCommand(command="start", description="Restart"),
        BotCommand(command="top", description="Top Popular Songs"),
        BotCommand(command="lang", description="Choose a language"),
        BotCommand(command="media_effect", description="Media effect"),
        BotCommand(command="about", description="About"),
    ]

    await bot.set_my_commands(commands=user_commands)

    admin_commands = user_commands + [
        BotCommand(command="admin_menu", description="Admin main menu")
    ]

    for admin_id in settings.admins_ids:
        scope = BotCommandScopeChat(chat_id=int(admin_id))
        await bot.set_my_commands(commands=admin_commands, scope=scope)