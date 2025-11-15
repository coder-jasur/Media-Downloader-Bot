import logging
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from asyncpg import Pool

from src.app.keyboards.inline import back_to_admin_menu_keyboards
from src.app.services.broadcaster import Broadcaster
from src.app.states.admin.broadcast import BroadcastingManagerSG
from src.app.utils.i18n import get_translator

logger = logging.getLogger(__name__)

broadcaster_router = Router()


def serialize_message(message: Message) -> dict:
    """Convert Message object to JSON-serializable dict"""
    data = {
        "message_id": message.message_id,
        "chat_id": message.chat.id,
        "text": message.text,
        "caption": message.caption,
    }

    # Add media information if present
    if message.photo:
        data["photo"] = message.photo[-1].file_id  # Highest resolution
    if message.video:
        data["video"] = message.video.file_id
    if message.document:
        data["document"] = message.document.file_id
    if message.audio:
        data["audio"] = message.audio.file_id
    if message.voice:
        data["voice"] = message.voice.file_id
    if message.animation:
        data["animation"] = message.animation.file_id
    if message.sticker:
        data["sticker"] = message.sticker.file_id
    if message.video_note:
        data["video_note"] = message.video_note.file_id

    # Add entities if present (for formatting)
    if message.entities:
        data["entities"] = [
            {
                "type": entity.type,
                "offset": entity.offset,
                "length": entity.length,
                "url": entity.url,
                "user": entity.user.id if entity.user else None,
                "language": entity.language,
            }
            for entity in message.entities
        ]

    if message.caption_entities:
        data["caption_entities"] = [
            {
                "type": entity.type,
                "offset": entity.offset,
                "length": entity.length,
                "url": entity.url,
                "user": entity.user.id if entity.user else None,
                "language": entity.language,
            }
            for entity in message.caption_entities
        ]

    return data


@broadcaster_router.callback_query(F.data == "boroadcasting")
async def start_broadcasting(call: CallbackQuery, state: FSMContext, lang: str):
    """Broadcasting boshlash"""
    _ = get_translator(lang).gettext

    await call.message.edit_text(
        _("Broadcasting start message"),
        parse_mode="HTML"
    )
    await state.set_state(BroadcastingManagerSG.get_message)


@broadcaster_router.message(BroadcastingManagerSG.get_message)
async def receive_broadcast_message(message: Message, state: FSMContext, lang: str, **kwargs):
    """Broadcasting xabarini qabul qilish"""
    _ = get_translator(lang).gettext

    # Poll qabul qilinmaydi
    if message.poll:
        await message.delete()
        await message.answer(_("Poll not allowed"))
        return

    # Album yoki yagona xabar
    album = kwargs.get("album")
    if album:
        # Serialize each message in album
        serialized_album = [serialize_message(msg) for msg in album]
        await state.update_data(album=serialized_album)
    else:
        # Serialize single message
        serialized_message = serialize_message(message)
        await state.update_data(message=serialized_message)

    await state.set_state(BroadcastingManagerSG.confirm_broadcasting)
    await message.answer(
        _("Message received confirm broadcasting"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=_("Cancel"),
                        callback_data="broadcast:cancel"
                    ),
                    InlineKeyboardButton(
                        text=_("Confirm"),
                        callback_data="broadcast:confirm"
                    ),
                ]
            ]
        )
    )


@broadcaster_router.callback_query(
    BroadcastingManagerSG.confirm_broadcasting,
    F.data == "broadcast:cancel"
)
async def cancel_broadcast(call: CallbackQuery, state: FSMContext, lang: str):
    """Broadcasting bekor qilish"""
    _ = get_translator(lang).gettext

    await state.clear()
    await call.message.edit_text(
        _("Broadcasting cancelled"),
        reply_markup=back_to_admin_menu_keyboards(lang)
    )


@broadcaster_router.callback_query(
    BroadcastingManagerSG.confirm_broadcasting,
    F.data == "broadcast:confirm"
)
async def confirm_broadcast(call: CallbackQuery, state: FSMContext, bot: Bot, pool: Pool, lang: str):
    """Broadcasting tasdiqlash va boshlash"""
    _ = get_translator(lang).gettext

    try:
        data = await state.get_data()
        message = data.get("message")
        album = data.get("album")

        if not (message or album):
            raise ValueError(_("Message not found"))

        await call.message.edit_text(_("Broadcasting started"))

        # Broadcaster yaratish
        broadcaster = Broadcaster(
            pool=pool,
            bot=bot,
            admin_id=call.from_user.id,
            broadcasting_message=message,  # Now a dict
            album=album,  # Now a list of dicts
            batch_size=5000,
            lang=lang
        )

        # Broadcasting
        blocked, deleted, limited, deactivated = await broadcaster.broadcast()

        # Natija - using string concatenation instead of .format()
        result_parts = [_("Broadcasting completed")]

        if blocked:
            # Use string formatting that matches your translation method
            blocked_msg = _("Blocked users count")
            result_parts.append(f"{blocked_msg}: {len(blocked)}")

        if deleted:
            deleted_msg = _("Deleted users count")
            result_parts.append(f"{deleted_msg}: {len(deleted)}")

        if limited:
            limited_msg = _("Limited users count")
            result_parts.append(f"{limited_msg}: {len(limited)}")

        if deactivated:
            deactivated_msg = _("Deactivated users count")
            result_parts.append(f"{deactivated_msg}: {len(deactivated)}")

        if not any([blocked, deleted, limited, deactivated]):
            result_parts.append(_("All messages delivered successfully"))

        result_text = "\n".join(result_parts)

        await call.message.edit_text(result_text, parse_mode="HTML")
        await state.clear()

    except ValueError as e:
        # Use f-string instead of .format()
        error_msg = _("Error")
        await call.message.edit_text(f"{error_msg}: {str(e)}")
        await state.clear()

    except Exception as e:
        logger.error(f"Broadcasting error: {e}")
        # Use f-string instead of .format()
        error_msg = _("Unexpected error")
        await call.message.edit_text(f"{error_msg}: {str(e)}")
        await state.clear()