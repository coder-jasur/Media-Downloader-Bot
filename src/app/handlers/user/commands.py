from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.app.keyboards.inline import auido_effect_kbd, songs_keyboard
from src.app.services.media_downloaders.seekers.search import YouTubeSearcher
from src.app.utils.i18n import get_translator

user_commands_router = Router()


@user_commands_router.message(Command("about"))
async def handled_command_about(message: Message, lang: str):
    _ = get_translator(lang).gettext
    await message.answer(_("About"))


@user_commands_router.message(Command("media_effect"))
async def handled_command_media_effect(message: Message, lang: str):
    _ = get_translator(lang).gettext
    await message.answer(
        _("Media effect"),
        reply_markup=auido_effect_kbd(
            actions="by_command",
            lang=lang
        )
    )


@user_commands_router.message(Command("top"))
async def handled_command_top(message: Message, lang: str):
    _ = get_translator(lang).gettext
    searcher = YouTubeSearcher()
    songs = await searcher.get_top_music()

    if not songs:
        await message.answer("Top musiqalarni olishda xatolik yuz berdi.")
        return

    page = 1

    text = _("Top songs")

    await message.answer(text, reply_markup=songs_keyboard(songs, page=page))


@user_commands_router.callback_query(F.data.startswith("page:"))
async def page_handler(callback: CallbackQuery, lang: str):
    _ = get_translator(lang).gettext

    searcher = YouTubeSearcher()
    songs = await searcher.get_top_music(limit=50)
    code, page_s = callback.data.split(":")
    page = int(page_s)
    kb = songs_keyboard(songs, page=page)

    await callback.message.edit_text(text=_("Top popular songs"), reply_markup=kb)

@user_commands_router.callback_query(F.data.in_(["close", "delete_list_music"]))
async def close_handler(callback: CallbackQuery):
    await callback.message.delete()
