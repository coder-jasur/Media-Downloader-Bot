import asyncio
import os
from pathlib import Path

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
        if path and await asyncio.to_thread(os.path.exists, path):
            try:
                await asyncio.to_thread(os.remove, path)
            except Exception as e:
                print(f"Cleanup error: {e}")


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



@media_downloader_router.message(F.text | F.video | F.video_note | F.voice | F.audio)
async def all_downloader_(message: Message, lang: str):
    _ = get_translator(lang).gettext

    for media in [message.audio, message.voice, message.video, message.video_note]:
        if media and media.file_size > 20 * 1024 * 1024:
            await message.answer(_("File is so big"))
            return

    video_path = None
    post_paths = None
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
                        highlights_path = await downloader.instagram_downloaders(
                            message.text, InstagramMediaType.HIGHLIGHT
                        )

                        if highlights_path:
                            for highlight_path in highlights_path:
                                await message.reply_video(
                                    FSInputFile(highlight_path),
                                    reply_markup=video_keyboards(lang),
                                    caption=_("Downloaded by")
                                )

                    elif info.url_type == URLType.INSTAGRAM_STORIES:
                        load_msg = await message.answer(_("Stories is loading"))
                        video_path = await downloader.instagram_downloaders(
                            message.text, InstagramMediaType.STORIES
                        )

                        if "photos" in str(video_path):
                            await message.reply_photo(
                                FSInputFile(video_path),
                                caption=_("Downloaded by")
                            )

                        elif "videos" in str(video_path):
                            await message.reply_video(
                                FSInputFile(video_path),
                                reply_markup=video_keyboards(lang),
                                caption=_("Downloaded by")
                            )

                    elif info.url_type == URLType.INSTAGRAM_POST:
                        load_msg = await message.answer(_("Post is loading"))
                        post_paths = await downloader.instagram_downloaders(
                            message.text, InstagramMediaType.POST
                        )

                        if post_paths:
                            for post in post_paths:
                                if not post:
                                    continue

                                if isinstance(post, list):
                                    media_group = []
                                    for i, media in enumerate(post):
                                        media_path = media.get("media_path")
                                        media_type = media.get("type")
                                        is_first = i == 0
                                        caption = _("Downloaded by") if is_first else None

                                        if not media_path or not await asyncio.to_thread(os.path.exists, media_path):
                                            continue

                                        if media_type == "video":
                                            media_group.append(
                                                InputMediaVideo(
                                                    media=FSInputFile(media_path),
                                                    caption=caption
                                                )
                                            )
                                        elif media_type == "photo":
                                            media_group.append(
                                                InputMediaPhoto(
                                                    media=FSInputFile(media_path),
                                                    caption=caption
                                                )
                                            )

                                    if media_group:
                                        await message.reply_media_group(media=media_group)

                                elif isinstance(post, dict):
                                    media_path = post.get("media_path")
                                    media_type = post.get("type")

                                    if not media_path or not await asyncio.to_thread(os.path.exists, media_path):
                                        continue

                                    if media_type == "video":
                                        await message.reply_video(
                                            FSInputFile(media_path),
                                            caption=_("Downloaded by"),
                                            reply_markup=video_keyboards(lang)
                                        )
                                    elif media_type == "photo":
                                        await message.reply_photo(
                                            FSInputFile(media_path),
                                            caption=_("Downloaded by")
                                        )

                    elif info.url_type in [
                        URLType.INSTAGRAM_REEL,
                        URLType.INSTAGRAM_IGTV,
                        URLType.INSTAGRAM_CDN_VIDEO
                    ]:
                        load_msg = await message.answer(_("Reels is loading"))
                        video_path = await downloader.instagram_downloaders(
                            message.text, InstagramMediaType.REELS
                        )

                        if video_path and await asyncio.to_thread(os.path.exists, video_path):
                            await message.reply_video(
                                FSInputFile(video_path),
                                reply_markup=video_keyboards(lang),
                                caption=_("Downloaded by")
                            )

                    elif info.url_type in [
                        URLType.INSTAGRAM_PROFILE_PHOTO,
                        URLType.INSTAGRAM_CDN_PHOTO
                    ]:
                        load_msg = await message.answer(_("Profil photo is loading"))
                        photo_path = await downloader.instagram_downloaders(
                            message.text, InstagramMediaType.PROFILE_PHOTO
                        )

                        if photo_path and await asyncio.to_thread(os.path.exists, photo_path):
                            await message.reply_photo(
                                FSInputFile(photo_path),
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

                        if video_path and await asyncio.to_thread(os.path.exists, video_path):
                            await message.reply_video(
                                FSInputFile(video_path),
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

                        if video_path and await asyncio.to_thread(os.path.exists, video_path):
                            await message.reply_video(
                                FSInputFile(video_path),
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

            # Media turini aniqlash
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

    except Exception as e:
        print(f"ERROR in all_downloader_: {e}")
        import traceback
        traceback.print_exc()
        await message.answer(_("Error in loading"))

    finally:
        if load_msg:
            try:
                await load_msg.delete()
            except Exception as e:
                print("ERROR deleting load_msg:", e)

        await cleanup_files(video_path, photo_path, thumbnail_path)
        await cleanup_post_paths(post_paths)

        if highlights_path:
            await cleanup_files(*highlights_path)


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
            await call.message.edit_text(_("Error in loading music"))
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
    audio_path = None
    video_path = None

    try:
        file = await bot.get_file(call.message.audio.file_id)
        file_path = file.file_path
        video_path = f"./media/videos/{get_video_file_name()}"

        await bot.download_file(file_path, video_path)
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
            if file and await asyncio.to_thread(os.path.exists, file):
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