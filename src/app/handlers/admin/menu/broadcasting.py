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
        await state.update_data(album=album)
    else:
        await state.update_data(message=message)

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
            broadcasting_message=message,
            album=album,
            batch_size=5000,
            lang=lang
        )

        # Broadcasting
        blocked, deleted, limited, deactivated = await broadcaster.broadcast()

        # Natija
        result_parts = [_("Broadcasting completed")]

        if blocked:
            result_parts.append(_("Blocked users count").format(count=len(blocked)))
        if deleted:
            result_parts.append(_("Deleted users count").format(count=len(deleted)))
        if limited:
            result_parts.append(_("Limited users count").format(count=len(limited)))
        if deactivated:
            result_parts.append(_("Deactivated users count").format(count=len(deactivated)))

        if not any([blocked, deleted, limited, deactivated]):
            result_parts.append(_("All messages delivered successfully"))

        result_text = "\n".join(result_parts)

        await call.message.edit_text(result_text, parse_mode="HTML")
        await state.clear()

    except ValueError as e:
        await call.message.edit_text(_("Error: {error}").format(error=str(e)))
        await state.clear()

    except Exception as e:
        logger.error(f"{_('Broadcasting error')}: {e}")
        await call.message.edit_text(_("Unexpected error: {error}").format(error=str(e)))
        await state.clear()