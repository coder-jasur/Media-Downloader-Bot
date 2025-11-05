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
from aiogram.types import Message, InputMedia
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
            broadcasting_message: Message = None,
            album: list[Message] = None,
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
            broadcasting_message: Yagona xabar
            album: Album xabarlari
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

            logger.info(
                self._("Broadcasting completed: {sent} sent, {failed} failed, {batches} batches").format(
                    sent=self.stats.sent,
                    failed=self.stats.failed,
                    batches=self.stats.batches
                )
            )

        except Exception as e:
            logger.error(f"{self._('Broadcasting error')}: {e}")
            await self.bot.send_message(
                self.admin_id,
                self._("Broadcasting error: {error}").format(error=str(e))
            )

        finally:
            await self._update_status_message(info_message, final=True)
            await self._delete_preview()
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
                await self.bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=self.broadcasting_message.from_user.id,
                    message_id=self.broadcasting_message.message_id,
                    reply_markup=self.broadcasting_message.reply_markup
                )
            else:
                await self.bot.send_media_group(
                    chat_id=user_id,
                    media=self._prepare_album(self.album)
                )

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
            logger.warning(
                self._("[ID:{user_id}] Flood limit. Sleeping {seconds}s").format(
                    user_id=user_id,
                    seconds=e.retry_after
                )
            )
            await asyncio.sleep(e.retry_after)
            return await self._send_to_user(user_id)

        except (TelegramBadRequest, TelegramAPIError) as e:
            logger.error(f"[ID:{user_id}] {self._('Telegram error')}: {e}")
            return False

        except Exception as e:
            logger.error(f"[ID:{user_id}] {self._('Unexpected error')}: {e}")
            return False

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
                    logger.info(
                        self._("{count} users marked as {status}").format(
                            count=len(user_ids),
                            status=status
                        )
                    )

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
                text += "\n\n" + self._("Total processed: {count} users").format(
                    count=self.stats.total_processed
                )

            await message.edit_text(text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"{self._('Status update error')}: {e}")

    def _format_status_text(self) -> str:
        """Status text formatlash"""
        return self._(
            "📤 <b>Broadcasting</b>\n\n"
            "✅ Sent: {sent}\n"
            "❌ Failed: {failed}\n"
            "🚫 Blocked: {blocked}\n"
            "🗑 Deleted: {deleted}\n"
            "⚠️ Limited: {limited}\n"
            "💤 Deactivated: {deactivated}\n"
            "📦 Batches: {batches}"
        ).format(
            sent=self.stats.sent,
            failed=self.stats.failed,
            blocked=self.stats.blocked,
            deleted=self.stats.deleted,
            limited=self.stats.limited,
            deactivated=self.stats.deactivated,
            batches=self.stats.batches
        )

    async def _delete_preview(self) -> None:
        """Preview xabarlarni o'chirish"""
        try:
            if self.broadcasting_message:
                await self.bot.delete_message(
                    self.admin_id,
                    self.broadcasting_message.message_id
                )
            elif self.album:
                await self.bot.delete_messages(
                    self.admin_id,
                    [msg.message_id for msg in self.album]
                )
        except Exception as e:
            logger.error(f"{self._('Preview delete error')}: {e}")

    def _prepare_album(self, album: list[Message]) -> list[InputMedia]:
        """Album tayyorlash"""
        from aiogram.types import (
            InputMediaPhoto,
            InputMediaVideo,
            InputMediaAnimation,
            InputMediaDocument,
            InputMediaAudio
        )

        media_list = []

        for message in album:
            media = None
            caption = getattr(message, 'html_text', None)
            has_spoiler = getattr(message, 'has_media_spoiler', None)

            if message.photo:
                media = InputMediaPhoto(
                    media=message.photo[-1].file_id,
                    caption=caption,
                    has_spoiler=has_spoiler
                )
            elif message.video:
                media = InputMediaVideo(
                    media=message.video.file_id,
                    caption=caption,
                    has_spoiler=has_spoiler
                )
            elif message.animation:
                media = InputMediaAnimation(
                    media=message.animation.file_id,
                    caption=caption,
                    has_spoiler=has_spoiler
                )
            elif message.document:
                media = InputMediaDocument(
                    media=message.document.file_id,
                    caption=caption
                )
            elif message.audio:
                media = InputMediaAudio(
                    media=message.audio.file_id,
                    caption=caption
                )

            if media:
                media_list.append(media)

        return media_list