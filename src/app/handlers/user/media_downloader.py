import asyncio
import os
from pathlib import Path
from typing import List

import aiofiles
import aiohttp
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery, InputMediaPhoto, InputMediaVideo, InputMediaAudio

from src.app.keyboards.callback_data import MusicCD, SearchMusicInVideoCD, AudioCD, MediaEffectsCD, TopPopularMusicCD
from src.app.keyboards.inline import video_keyboards, music_keyboards, audio_keyboard, auido_effect_kbd
from src.app.services.media_downloaders.all_downloader import AllDownloader
from src.app.services.media_downloaders.utils.files import get_video_file_name
from src.app.services.media_effects.media_effects import MediaEffects
from src.app.states.user.media_effect import SendMediaSG
from src.app.utils.enums.audio import MusicAction
from src.app.utils.enums.general import GeneralEffectAction, MediaType
from src.app.utils.enums.url import URLType
from src.app.utils.enums.video import InstagramMediaType
from src.app.utils.i18n import get_translator
from src.app.utils.url_validators import SocialMediaURLValidator

media_downloader_router = Router()


@media_downloader_router.callback_query(MediaEffectsCD.filter())
async def take_media_effect(call: CallbackQuery, callback_data: MediaEffectsCD, bot: Bot, state: FSMContext, lang: str):
    _ = get_translator(lang).gettext
    if callback_data.actions == "by_command":
        await state.update_data({"media_effect_type": callback_data.effect})
        await state.set_state(SendMediaSG.send_media)
        await call.message.edit_text(_("Send media"))
    else:
        load_msg = await call.message.answer(_("Is being processed"))
        media_effect = MediaEffects(message=call.message, bot=bot)
        out_put_media_path = None

        try:
            effect_str = callback_data.effect.value
            if not effect_str:
                await call.message.answer(_("Effec type not found"))
                return

            try:
                general_effect_type = GeneralEffectAction(effect_str)
            except Exception as e:
                print("ERROR", e)
                mapping = {
                    "8d": GeneralEffectAction.EFFECT_8D,
                    "slowed": GeneralEffectAction.EFFECT_SLOWED,
                    "speed": GeneralEffectAction.EFFECT_SPEED,
                    "concert_hall": GeneralEffectAction.EFFECT_CONCERT_HALL
                }
                general_effect_type = mapping.get(effect_str)

            if call.message.video:
                meida_type = MediaType.VIDEO
            elif call.message.audio:
                meida_type = MediaType.AUDIO
            elif call.message.voice:
                meida_type = MediaType.VOICE
            else:
                await call.message.answer(_("Media type not found"))
                return

            out_put_media_path = await media_effect.media_effect(
                effect_type=general_effect_type,
                media_type=meida_type,
            )

            if not out_put_media_path or not await asyncio.to_thread(os.path.exists, out_put_media_path):
                await call.message.answer(_("Error in processed media"))
                return

            if meida_type == MediaType.VIDEO:
                await call.message.answer_video(
                    FSInputFile(out_put_media_path),
                    caption=_("Downloaded by"),
                    title="effect video"
                )
            else:
                audio_title = None
                if call.message.audio and getattr(call.message.audio, "title", None):
                    audio_title = call.message.audio.title

                effect_name = effect_str or (general_effect_type.value if general_effect_type else "")
                title_text = f"{audio_title} {effect_name} remix" if audio_title else f"voice {effect_name} remix"

                await call.message.edit_media(
                    InputMediaAudio(
                        media=FSInputFile(out_put_media_path),
                        caption=_("Downloaded by"),
                        title=title_text
                    )
                )
        except Exception as e:
            print("ERROR in take_media_effect:", e)
            await call.message.answer(_("Error in processed media"))
        finally:
            await state.clear()
            try:
                if out_put_media_path and await asyncio.to_thread(os.path.exists, out_put_media_path):
                    await asyncio.to_thread(os.remove, out_put_media_path)
            except Exception as ex:
                print("Final cleanup error:", ex)
            if load_msg:
                try:
                    await load_msg.delete()
                except Exception as e:
                    print("ERROR deleting load_msg:", e)


@media_downloader_router.message(SendMediaSG.send_media)
async def take_media(message: Message, state: FSMContext, bot: Bot, lang: str):
    _ = get_translator(lang).gettext
    load_msg = await message.answer(_("Is being processed"))
    media_effect = MediaEffects(message=message, bot=bot)
    data = await state.get_data()
    out_put_media_path = None

    try:
        effect_str = data.get("media_effect_type")
        if not effect_str:
            await message.answer(_("Effect type not found"))
            return

        try:
            general_effect_type = GeneralEffectAction(effect_str)
        except Exception as e:
            print("ERROR", e)
            mapping = {
                "8d": GeneralEffectAction.EFFECT_8D,
                "slowed": GeneralEffectAction.EFFECT_SLOWED,
                "speed": GeneralEffectAction.EFFECT_SPEED,
                "concert_hall": GeneralEffectAction.EFFECT_CONCERT_HALL
            }
            general_effect_type = mapping.get(effect_str)

        if message.video:
            meida_type = MediaType.VIDEO
        elif message.audio:
            meida_type = MediaType.AUDIO
        elif message.voice:
            meida_type = MediaType.VOICE
        else:
            await message.answer(_("Media type not found"))
            return

        out_put_media_path = await media_effect.media_effect(
            effect_type=general_effect_type,
            media_type=meida_type,
        )

        if not out_put_media_path or not await asyncio.to_thread(os.path.exists, out_put_media_path):
            await message.answer(_("Error in processed media"))
            return

        if meida_type == MediaType.VIDEO:
            await message.answer_video(
                FSInputFile(out_put_media_path),
                caption=_("Downloaded by"),
                title="effect video"
            )
        else:
            audio_title = None
            if message.audio and getattr(message.audio, "title", None):
                audio_title = message.audio.title

            effect_name = effect_str or (general_effect_type.value if general_effect_type else "")
            title_text = f"{audio_title} {effect_name} remix" if audio_title else f"voice {effect_name} remix"

            await message.answer_audio(
                audio=FSInputFile(out_put_media_path),
                caption=_("Downloaded by"),
                title=title_text
            )

    except Exception as e:
        print("ERROR in take_media:", e)
        await message.answer(_("Error in processed"))
    finally:
        await state.clear()
        try:
            if out_put_media_path and await asyncio.to_thread(os.path.exists, out_put_media_path):
                await asyncio.to_thread(os.remove, out_put_media_path)
        except Exception as ex:
            print("Final cleanup error:", ex)
        if load_msg:
            try:
                await load_msg.delete()
            except Exception as e:
                print("ERROR deleting load_msg:", e)


async def cleanup_files(*file_paths):
    for path in file_paths:
        if path is None:
            continue

        if isinstance(path, (list, tuple)):
            for item in path:
                if item:
                    try:
                        item_str = str(item)
                        exists = await asyncio.to_thread(os.path.exists, item_str)
                        if exists:
                            await asyncio.to_thread(os.remove, item_str)
                    except Exception as e:
                        print(f"ERROR: {e}")
        else:
            if path:
                try:
                    path_str = str(path)
                    exists = await asyncio.to_thread(os.path.exists, path_str)
                    if exists:
                        await asyncio.to_thread(os.remove, path_str)
                except Exception as e:
                    print(f"ERROR: {e}")


async def cleanup_post_paths(post_paths):
    if not post_paths:
        return

    for post in post_paths:
        if isinstance(post, dict):
            path = post.get("media_path")
            if isinstance(path, str):
                await cleanup_files(path)
            elif isinstance(path, list):
                await cleanup_files(*path)
        elif isinstance(post, list):
            await cleanup_files(*post)


def create_media_group(media_list: List[str], caption: str = None) -> List:
    """Media guruhini yaratish"""
    media_group = []

    for i, post in enumerate(media_list):
        if not post:
            continue
        if not Path(post).exists():
            continue

        media_caption = caption if i == 0 else None
        ext = os.path.splitext(post)[1].lower()

        try:
            if ext in [".jpg", ".jpeg", ".png", ".webp"]:
                media_group.append(InputMediaPhoto(media=FSInputFile(post), caption=media_caption))
            elif ext in [".mp4", ".mov", ".mkv"]:
                media_group.append(InputMediaVideo(media=FSInputFile(post), caption=media_caption))
        except Exception as e:
            print(f"ERROR: {e}")

    return media_group


@media_downloader_router.message(F.text | F.video | F.video_note | F.voice | F.audio)
async def all_downloader_(message: Message, lang: str):
    _ = get_translator(lang).gettext

    for media in [message.audio, message.voice, message.video, message.video_note]:
        if media and media.file_size > 20 * 1024 * 1024:
            await message.answer(_("File is so big"))
            return

    video_path = None
    photo_path = None
    thumbnail_path = None
    highlights_path = None
    load_msg = None
    downloader = AllDownloader(message=message, lang=lang)

    try:
        if message.text:
            if message.text.startswith("https://"):
                validator = SocialMediaURLValidator()
                info = await asyncio.to_thread(validator.validate, message.text)

                if info.platform == "instagram":
                    if info.url_type == URLType.INSTAGRAM_HIGHLIGHT:
                        load_msg = await message.answer(_("Highlight is loading"))
                        urls = await downloader.instagram_downloaders(
                            message.text, InstagramMediaType.HIGHLIGHT
                        )

                        if urls:
                            if ".jpeg" in str(urls):
                                for url in urls:
                                    await message.reply_photo(
                                        url,
                                        caption=_("Downloaded by")
                                    )

                            elif ".mp4" in str(urls):
                                for url in urls:
                                    await message.reply_video(
                                        url,
                                        reply_markup=video_keyboards(lang),
                                        caption=_("Downloaded by")
                                    )

                    elif info.url_type == URLType.INSTAGRAM_STORIES:
                        load_msg = await message.answer(_("Stories is loading"))
                        urls = await downloader.instagram_downloaders(
                            message.text, InstagramMediaType.STORIES
                        )
                        if urls:
                            if ".jpeg" in str(urls):
                                for url in urls:
                                    await message.reply_photo(
                                        url,
                                        caption=_("Downloaded by")
                                    )


                            elif ".mp4" in str(urls):
                                for url in urls:
                                    await message.reply_video(
                                        url,
                                        reply_markup=video_keyboards(lang),
                                        caption=_("Downloaded by")
                                    )


                    elif info.url_type == URLType.INSTAGRAM_POST:
                        load_msg = await message.answer(_("Post is loading"))

                        urls = await downloader.instagram_downloaders(
                            message.text, InstagramMediaType.POST
                        )

                        if not urls:
                            return

                        skipped = []

                        for url in urls:
                            if not url:
                                continue

                            media_type = MediaType.VIDEO if "mp4" in url else MediaType.PHOTO

                            if media_type == MediaType.PHOTO:
                                try:
                                    caption = _("Downloaded by")
                                    await message.reply_photo(
                                        url,
                                        caption=caption
                                    )

                                except Exception as e:
                                    print(f"ERROR: {e}")
                                    skipped.append(url)

                            elif media_type == MediaType.VIDEO:
                                try:
                                    await message.reply_video(
                                        url,
                                        reply_markup=video_keyboards(lang)
                                    )

                                except Exception as e:
                                    print(f"ERROR: {e}")
                                    skipped.append(url)

                    elif info.url_type in [
                        URLType.INSTAGRAM_REEL,
                        URLType.INSTAGRAM_IGTV,
                        URLType.INSTAGRAM_CDN_VIDEO
                    ]:
                        load_msg = await message.answer(_("Reels is loading"))
                        video_path = await downloader.instagram_downloaders(
                            message.text, InstagramMediaType.REELS
                        )

                        if video_path and await asyncio.to_thread(os.path.exists, str(video_path)):
                            await message.reply_video(
                                FSInputFile(str(video_path)),
                                reply_markup=video_keyboards(lang),
                                caption=_("Downloaded by")
                            )

                    elif info.url_type in [
                        URLType.INSTAGRAM_PROFILE_PHOTO,
                        URLType.INSTAGRAM_CDN_PHOTO
                    ]:
                        load_msg = await message.answer(_("Profile photo is loading"))
                        photo_path = await downloader.instagram_downloaders(
                            message.text, InstagramMediaType.PROFILE_PHOTO
                        )

                        if photo_path and await asyncio.to_thread(os.path.exists, str(photo_path)):
                            await message.reply_photo(
                                FSInputFile(str(photo_path)),
                                caption=_("Downloaded by")
                            )

                    else:
                        await message.answer(_("Wrong url"))

                elif info.platform == "youtube":
                    if info.url_type in [
                        URLType.YOUTUBE_VIDEO,
                        URLType.YOUTUBE_SHORTS,
                        URLType.YOUTUBE_LIVE,
                        URLType.YOUTUBE_CDN_VIDEO
                    ]:
                        load_msg = await message.answer(_("Video is loading"))
                        url_to_download = info.clean_url or message.text
                        video_path = await downloader.youtube_downloaders(url_to_download)
                        print(video_path)

                        if video_path and await asyncio.to_thread(os.path.exists, str(video_path)):
                            await message.reply_video(
                                FSInputFile(str(video_path)),
                                reply_markup=video_keyboards(lang),
                                caption=_("Downloaded by")
                            )
                    else:
                        await message.answer(_("Wrong url"))

                elif info.platform == "tiktok":
                    if info.url_type in [
                        URLType.TIKTOK_VIDEO,
                        URLType.TIKTOK_PHOTO,
                        URLType.TIKTOK_CDN_VIDEO
                    ]:
                        load_msg = await message.answer(_("Video is loading"))
                        video_path = await downloader.tiktok_downloaders(message.text)

                        if video_path and await asyncio.to_thread(os.path.exists, str(video_path)):
                            await message.reply_video(
                                FSInputFile(str(video_path)),
                                reply_markup=video_keyboards(lang),
                                caption=_("Downloaded by")
                            )
                    else:
                        await message.answer(_("Wrong url"))

                else:
                    await message.answer(_("Wrong url"))

            else:
                load_msg = await message.answer(_("Music is loading"))
                music_list, music_title, thumbnail_path = await downloader.music_downloaders(
                    MusicAction.SEARCH_BY_TEXT,
                    some_data=message.text
                )

                if music_list:
                    if thumbnail_path and await asyncio.to_thread(Path(thumbnail_path).exists):
                        await message.reply_photo(
                            photo=FSInputFile(thumbnail_path),
                            caption=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
                    else:
                        await message.reply(
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )

        elif message.video or message.video_note or message.audio or message.voice:
            load_msg = await message.answer(_("Music is loading"))

            media_type = None
            if message.video:
                media_type = MediaType.VIDEO
            elif message.video_note:
                media_type = MediaType.VIDEO_NOTE
            elif message.audio:
                media_type = MediaType.AUDIO
            elif message.voice:
                media_type = MediaType.VOICE

            if media_type:
                music_list, music_title, thumbnail_path = await downloader.music_downloaders(
                    MusicAction.SEARCH_BY_MEDIA,
                    media_type=media_type
                )

                if music_list:
                    if thumbnail_path and await asyncio.to_thread(os.path.exists, thumbnail_path):
                        await message.reply_photo(
                            photo=FSInputFile(thumbnail_path),
                            caption=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
                    else:
                        await message.reply(
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )

    except Exception as e:
        print(f"ERROR: {e}")
        await message.answer(_("Error in loading"))

    finally:
        if load_msg:
            try:
                await load_msg.delete()
            except Exception as e:
                print(f"ERROR: {e}")

        await cleanup_files(video_path, photo_path, thumbnail_path)

        if highlights_path:
            await cleanup_files(highlights_path)


@media_downloader_router.callback_query(SearchMusicInVideoCD.filter())
async def send_music_results_from_video(call: CallbackQuery, lang: str):
    _ = get_translator(lang).gettext
    load_msg = await call.message.answer(_("Music is loading"))
    all_downloader = AllDownloader(call.message)
    thumbnail_path = None
    try:
        musics_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
            actions=MusicAction.SEARCH_BY_MEDIA,
            media_type=MediaType.VIDEO
        )

        if musics_list:
            if thumbnail_path and await asyncio.to_thread(Path(thumbnail_path).exists):
                await call.message.reply_photo(
                    photo=FSInputFile(thumbnail_path),
                    caption=music_title,
                    reply_markup=music_keyboards(musics_list)
                )
            else:
                await call.message.reply(
                    text=music_title,
                    reply_markup=music_keyboards(musics_list)
                )
        else:
            await call.message.answer(_("Error in loading music"))
    except Exception as e:
        print("ERROR in send_music_results_from_video:", e)
        await call.message.answer(_("Error in loading music"))
    finally:
        if thumbnail_path and await asyncio.to_thread(os.path.exists, thumbnail_path):
            await asyncio.to_thread(os.remove, thumbnail_path)
        if load_msg:
            try:
                await load_msg.delete()
            except Exception as e:
                print("ERROR deleting load_msg:", e)


@media_downloader_router.callback_query(MusicCD.filter())
async def send_music_search_results(call: CallbackQuery, callback_data: MusicCD, lang: str):
    _ = get_translator(lang).gettext
    load_msg = await call.message.answer(_("Music is loading"))
    download_music = AllDownloader()
    music_path = None
    try:
        music_path, title = await download_music.music_downloaders(
            actions=MusicAction.DOWNLOAD,
            some_data=callback_data.video_id
        )

        if music_path and await asyncio.to_thread(os.path.exists, music_path):
            await call.message.reply_audio(
                audio=FSInputFile(music_path),
                title=title,
                caption=_("Downloaded by"),
                reply_markup=audio_keyboard(lang)
            )
    except Exception as e:
        print("ERROR in send_music_search_results:", e)
        await call.message.answer(text=_("Error in loading music"))
    finally:
        if load_msg:
            try:
                await load_msg.delete()
            except Exception as e:
                print("ERROR deleting load_msg:", e)
        if music_path and await asyncio.to_thread(os.path.exists, music_path):
            await asyncio.to_thread(os.remove, music_path)


@media_downloader_router.callback_query(TopPopularMusicCD.filter())
async def send_music_by_name(call: CallbackQuery, lang: str, callback_data: TopPopularMusicCD):
    _ = get_translator(lang).gettext
    downloader = AllDownloader()
    load_msg = await call.message.answer(_("Music is loading"))
    thumbnail_path = None
    try:
        music_list, music_title, thumbnail_path = await downloader.music_downloaders(
            MusicAction.SEARCH_BY_TEXT,
            some_data=callback_data.music_name
        )

        if music_list:
            if thumbnail_path and await asyncio.to_thread(Path(thumbnail_path).exists):
                await call.message.reply_photo(
                    photo=FSInputFile(thumbnail_path),
                    caption=music_title,
                    reply_markup=music_keyboards(music_list)
                )
            else:
                await call.message.reply(
                    text=music_title,
                    reply_markup=music_keyboards(music_list)
                )
    except Exception as e:
        print("ERROR in send_music_by_name:", e)
        await call.message.answer(_("Error in loading music"))
    finally:
        if load_msg:
            try:
                await load_msg.delete()
            except Exception as e:
                print("ERROR deleting load_msg:", e)
        if thumbnail_path and await asyncio.to_thread(os.path.exists, thumbnail_path):
            await asyncio.to_thread(os.remove, thumbnail_path)


@media_downloader_router.callback_query(AudioCD.filter())
async def send_video_mp3_audio_version(call: CallbackQuery, lang: str, bot: Bot):
    _ = get_translator(lang).gettext
    load_msg = await call.message.answer(text=_("Audio is loading"))
    downloader_audio = AllDownloader()
    video_path = f"./media/videos/{get_video_file_name()}"
    audio_path = None

    try:

        file = await bot.get_file(call.message.video.file_id)
        file_info = await bot.get_file(file.file_id)

        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{call.message.bot.token}/getFile?file_id={file_info.file_id}"
            async with session.get(url) as resp:
                file_info = await resp.json()
                file_path = file_info['result']['file_path']

            file_url = f"https://api.telegram.org/file/bot{call.message.bot.token}/{file_path}"
            async with session.get(file_url) as response:
                if response.status == 200:
                    async with aiofiles.open(video_path, "wb") as f:
                        await f.write(await response.read())

        audio_path = await downloader_audio.extract_video_to_audio(video_path)

        if audio_path and await asyncio.to_thread(os.path.exists, audio_path):
            await call.message.answer_audio(
                FSInputFile(audio_path),
                caption=_("Downloaded by"),
                title="mp3"
            )

    except Exception as e:
        print("ERROR in send_video_mp3_audio_version:", e)
        await call.message.answer(text=_("Error in loading audio"))

    finally:
        if load_msg:
            try:
                await load_msg.delete()
            except Exception as e:
                print("ERROR deleting load_msg:", e)

        for file in [audio_path, video_path]:
            if await asyncio.to_thread(os.path.exists, file):
                await asyncio.to_thread(os.remove, file)


@media_downloader_router.callback_query(F.data == "effects")
async def audio_effects(call: CallbackQuery, lang: str):
    _ = get_translator(lang).gettext
    try:
        if not call.message.audio:
            await call.message.answer(_("Audio not found"))
            return

        audio_file_id = call.message.audio.file_id
        await call.message.answer_audio(
            audio_file_id,
            caption=_("Choose effect"),
            reply_markup=auido_effect_kbd(
                actions="for_downloading_audio",
                lang=lang
            )
        )
    except Exception as e:
        print("ERROR", e)
        await call.answer(_("Error"))
