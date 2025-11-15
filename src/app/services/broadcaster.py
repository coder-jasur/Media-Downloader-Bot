import asyncio
import logging
from typing import Optional, Union
from dataclasses import dataclass, field

from aiogram import Bot, types
from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramRetryAfter,
    TelegramAPIError
)
from aiogram.types import Message, InputMedia, MessageEntity
from asyncpg import Pool

from src.app.database.queries.users import UserDataBaseActions
from src.app.utils.i18n import get_translator

logger = logging.getLogger(__name__)


@dataclass
class BroadcastStats:
    """Broadcasting statistika"""
    sent: int = 0
    failed: int = 0
    blocked: int = 0
    deleted: int = 0
    limited: int = 0
    deactivated: int = 0
    batches: int = 0
    total_processed: int = 0

    blocked_users: list[int] = field(default_factory=list)
    deleted_users: list[int] = field(default_factory=list)
    limited_users: list[int] = field(default_factory=list)
    deactivated_users: list[int] = field(default_factory=list)


class Broadcaster:
    """Optimized Broadcasting Service"""

    def __init__(
            self,
            pool: Pool,
            bot: Bot,
            admin_id: int,
            broadcasting_message: dict = None,
            album: list[dict] = None,
            batch_size: int = 5000,
            sleep_seconds: float = 0.04,
            lang: str = "uz"
    ):
        """
        Broadcasting service

        Args:
            pool: Database connection pool
            bot: Telegram Bot
            admin_id: Admin ID
            broadcasting_message: Serialized message dict
            album: List of serialized message dicts
            batch_size: Batch hajmi
            sleep_seconds: Xabarlar orasidagi kutish vaqti
            lang: Til kodi
        """
        self.pool = pool
        self.bot = bot
        self.admin_id = admin_id
        self.broadcasting_message = broadcasting_message
        self.album = album
        self.batch_size = batch_size
        self.sleep_seconds = sleep_seconds
        self.lang = lang
        self._ = get_translator(lang).gettext

        # Statistika
        self.stats = BroadcastStats()

        # Validation
        if not (broadcasting_message or album):
            raise ValueError(self._("Broadcasting message or album required"))
        if broadcasting_message and album:
            raise ValueError(self._("Choose only one: message or album"))

    async def broadcast(self) -> tuple[list[int], list[int], list[int], list[int]]:
        """
        Broadcasting boshlash

        Returns:
            (blocked_users, deleted_users, limited_users, deactivated_users)
        """
        info_message = await self._send_status_message()

        try:
            logger.info(self._("Broadcasting started"))

            user_actions = UserDataBaseActions(self.pool)

            async for user_ids, offset in user_actions.iterate_user_ids(self.batch_size):
                await self._process_batch(user_ids)
                self.stats.batches += 1
                self.stats.total_processed += len(user_ids)

                # Status update
                await self._update_status_message(info_message)

                # Database update
                await self._update_user_statuses()

            # Use f-string instead of .format() to avoid i18n issues
            logger.info(
                f"{self._('Broadcasting completed')}: "
                f"{self.stats.sent} sent, {self.stats.failed} failed, {self.stats.batches} batches"
            )

        except Exception as e:
            logger.error(f"{self._('Broadcasting error')}: {e}")
            await self.bot.send_message(
                self.admin_id,
                f"{self._('Broadcasting error')}: {str(e)}"
            )

        finally:
            await self._update_status_message(info_message, final=True)
            await self._update_user_statuses()

        return (
            self.stats.blocked_users,
            self.stats.deleted_users,
            self.stats.limited_users,
            self.stats.deactivated_users
        )

    async def _process_batch(self, user_ids: list[int]) -> None:
        """Batch jarayoni"""
        for user_id in user_ids:
            result = await self._send_to_user(user_id)

            if result is True:
                self.stats.sent += 1
            else:
                self.stats.failed += 1
                self._categorize_failure(user_id, result)

            await asyncio.sleep(self.sleep_seconds)

    def _reconstruct_entities(self, entities_data: list[dict]) -> list[MessageEntity]:
        """Reconstruct MessageEntity objects from serialized data"""
        if not entities_data:
            return None

        entities = []
        for entity_data in entities_data:
            entity = MessageEntity(
                type=entity_data["type"],
                offset=entity_data["offset"],
                length=entity_data["length"],
                url=entity_data.get("url"),
                user=entity_data.get("user"),
                language=entity_data.get("language")
            )
            entities.append(entity)
        return entities

    async def _send_to_user(self, user_id: int) -> Union[bool, str]:
        """
        Foydalanuvchiga xabar yuborish

        Returns:
            True - muvaffaqiyatli
            "blocked" - foydalanuvchi bloklagan
            "deleted" - akkaunt o'chirilgan
            "limited" - akkaunt cheklangan
            "deactivated" - akkaunt deaktivatsiya qilingan
            False - boshqa xato
        """
        try:
            if self.broadcasting_message:
                await self._send_single_message(user_id, self.broadcasting_message)
            else:
                await self._send_album(user_id, self.album)

            logger.debug(f"[ID:{user_id}] {self._('message sent')}")
            return True

        except TelegramForbiddenError as e:
            error_msg = str(e).lower()

            if "deactivated" in error_msg:
                logger.warning(f"[ID:{user_id}] {self._('deactivated')}")
                return "deactivated"
            elif "limited" in error_msg:
                logger.warning(f"[ID:{user_id}] {self._('limited')}")
                return "limited"
            elif "not found" in error_msg:
                logger.warning(f"[ID:{user_id}] {self._('deleted')}")
                return "deleted"
            else:
                logger.warning(f"[ID:{user_id}] {self._('blocked')}")
                return "blocked"

        except TelegramRetryAfter as e:
            logger.warning(f"[ID:{user_id}] Flood limit. Sleeping {e.retry_after}s")
            await asyncio.sleep(e.retry_after)
            return await self._send_to_user(user_id)

        except (TelegramBadRequest, TelegramAPIError) as e:
            logger.error(f"[ID:{user_id}] {self._('Telegram error')}: {e}")
            return False

        except Exception as e:
            logger.error(f"[ID:{user_id}] {self._('Unexpected error')}: {e}")
            return False

    async def _send_single_message(self, user_id: int, message_data: dict) -> None:
        """Send a single message based on serialized data"""
        # Reconstruct entities
        entities = self._reconstruct_entities(message_data.get("entities"))
        caption_entities = self._reconstruct_entities(message_data.get("caption_entities"))

        # Send based on content type
        if message_data.get("photo"):
            await self.bot.send_photo(
                chat_id=user_id,
                photo=message_data["photo"],
                caption=message_data.get("caption"),
                caption_entities=caption_entities
            )
        elif message_data.get("video"):
            await self.bot.send_video(
                chat_id=user_id,
                video=message_data["video"],
                caption=message_data.get("caption"),
                caption_entities=caption_entities
            )
        elif message_data.get("animation"):
            await self.bot.send_animation(
                chat_id=user_id,
                animation=message_data["animation"],
                caption=message_data.get("caption"),
                caption_entities=caption_entities
            )
        elif message_data.get("document"):
            await self.bot.send_document(
                chat_id=user_id,
                document=message_data["document"],
                caption=message_data.get("caption"),
                caption_entities=caption_entities
            )
        elif message_data.get("audio"):
            await self.bot.send_audio(
                chat_id=user_id,
                audio=message_data["audio"],
                caption=message_data.get("caption"),
                caption_entities=caption_entities
            )
        elif message_data.get("voice"):
            await self.bot.send_voice(
                chat_id=user_id,
                voice=message_data["voice"],
                caption=message_data.get("caption"),
                caption_entities=caption_entities
            )
        elif message_data.get("video_note"):
            await self.bot.send_video_note(
                chat_id=user_id,
                video_note=message_data["video_note"]
            )
        elif message_data.get("sticker"):
            await self.bot.send_sticker(
                chat_id=user_id,
                sticker=message_data["sticker"]
            )
        elif message_data.get("text"):
            await self.bot.send_message(
                chat_id=user_id,
                text=message_data["text"],
                entities=entities
            )

    async def _send_album(self, user_id: int, album_data: list[dict]) -> None:
        """Send album based on serialized data"""
        media_group = self._prepare_album(album_data)
        await self.bot.send_media_group(
            chat_id=user_id,
            media=media_group
        )

    def _categorize_failure(self, user_id: int, result: str) -> None:
        """Xatolikni kategoriyalash"""
        if result == "blocked":
            self.stats.blocked_users.append(user_id)
            self.stats.blocked += 1
        elif result == "deleted":
            self.stats.deleted_users.append(user_id)
            self.stats.deleted += 1
        elif result == "limited":
            self.stats.limited_users.append(user_id)
            self.stats.limited += 1
        elif result == "deactivated":
            self.stats.deactivated_users.append(user_id)
            self.stats.deactivated += 1

    async def _update_user_statuses(self) -> None:
        """Database'dagi foydalanuvchi statuslarini yangilash"""
        try:
            status_mapping = [
                (self.stats.blocked_users, "blocked"),
                (self.stats.deleted_users, "deleted"),
                (self.stats.limited_users, "limited"),
                (self.stats.deactivated_users, "deactivated"),
            ]

            for user_ids, status in status_mapping:
                if user_ids:
                    await self._batch_update_status(user_ids, status)
                    logger.info(f"{len(user_ids)} users marked as {status}")

            # Listlarni tozalash
            self.stats.blocked_users.clear()
            self.stats.deleted_users.clear()
            self.stats.limited_users.clear()
            self.stats.deactivated_users.clear()

        except Exception as e:
            logger.error(f"{self._('Status update error')}: {e}")

    async def _batch_update_status(self, user_ids: list[int], status: str) -> None:
        """Batch status update"""
        query = """
            UPDATE users 
            SET status = $1 
            WHERE tg_id = ANY($2::bigint[])
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, status, user_ids)

    async def _send_status_message(self) -> Message:
        """Status xabarini yuborish"""
        return await self.bot.send_message(
            self.admin_id,
            self._format_status_text(),
            parse_mode="HTML"
        )

    async def _update_status_message(self, message: Message, final: bool = False) -> None:
        """Status xabarini yangilash"""
        try:
            text = self._format_status_text()
            if final:
                text += f"\n\n{self._('Total processed')}: {self.stats.total_processed} users"

            await message.edit_text(text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"{self._('Status update error')}: {e}")

    def _format_status_text(self) -> str:
        """Status text formatlash"""
        # Use f-string to avoid .format() issues with translations
        return (
            f"📤 <b>{self._('Broadcasting')}</b>\n\n"
            f"✅ {self._('Sent')}: {self.stats.sent}\n"
            f"❌ {self._('Failed')}: {self.stats.failed}\n"
            f"🚫 {self._('Blocked')}: {self.stats.blocked}\n"
            f"🗑 {self._('Deleted')}: {self.stats.deleted}\n"
            f"⚠️ {self._('Limited')}: {self.stats.limited}\n"
            f"💤 {self._('Deactivated')}: {self.stats.deactivated}\n"
            f"📦 {self._('Batches')}: {self.stats.batches}"
        )

    def _prepare_album(self, album_data: list[dict]) -> list[InputMedia]:
        """Album tayyorlash from serialized data"""
        from aiogram.types import (
            InputMediaPhoto,
            InputMediaVideo,
            InputMediaAnimation,
            InputMediaDocument,
            InputMediaAudio
        )

        media_list = []

        for message_data in album_data:
            media = None
            caption = message_data.get("caption")
            caption_entities = self._reconstruct_entities(message_data.get("caption_entities"))

            if message_data.get("photo"):
                media = InputMediaPhoto(
                    media=message_data["photo"],
                    caption=caption,
                    caption_entities=caption_entities
                )
            elif message_data.get("video"):
                media = InputMediaVideo(
                    media=message_data["video"],
                    caption=caption,
                    caption_entities=caption_entities
                )
            elif message_data.get("animation"):
                media = InputMediaAnimation(
                    media=message_data["animation"],
                    caption=caption,
                    caption_entities=caption_entities
                )
            elif message_data.get("document"):
                media = InputMediaDocument(
                    media=message_data["document"],
                    caption=caption,
                    caption_entities=caption_entities
                )
            elif message_data.get("audio"):
                media = InputMediaAudio(
                    media=message_data["audio"],
                    caption=caption,
                    caption_entities=caption_entities
                )

            if media:
                media_list.append(media)

        return media_list