import asyncpg
from aiogram import Bot
from aiogram.filters import Filter, BaseFilter
from aiogram.types import Message, CallbackQuery
from asyncpg import Connection

from src.app.database.queries.channels import ChannelDataBaseActions


class CheckSubscription(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, pool: asyncpg.Pool, bot: Bot, **kwargs):
        channel_actions = ChannelDataBaseActions(pool)
        channel_data = await channel_actions.get_all_channels()

        if not channel_data:
            return False

        for channel in channel_data:

            if channel[3] == "True":
                user_status = await bot.get_chat_member(channel[0], event.from_user.id)
                if user_status.status not in ["member", "administrator", "creator"]:
                    return True
        return False
