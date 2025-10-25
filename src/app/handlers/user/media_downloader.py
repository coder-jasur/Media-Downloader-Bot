import asyncio
import os

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery, InputMediaPhoto, InputMediaVideo, InputMediaAudio

from src.app.keyboards.callback_data import MusicCD, SearchMusicInVideoCD, AudioCD, MediaEffectsCD
from src.app.keyboards.inline import video_keyboards, music_keyboards, audio_keyboard, auido_effect_kbd
from src.app.services.media_downloaders.all_downloader import AllDownloader
from src.app.services.media_downloaders.utils.files import get_video_file_name
from src.app.services.media_effects.media_effects import MediaEffects
from src.app.states.user.media_effect import SendMediaSG
from src.app.texts import (
    media_process_text, user_texts, video_process_texts, music_and_audio_process_texts,
    photo_process_texts
)
from src.app.utils.enums.audio import MusicAction
from src.app.utils.enums.general import GeneralEffectAction, MediaType
from src.app.utils.enums.video import InstagramMediaType
from src.app.utils.url_validators import validator_urls, SocialMediaURLValidator

media_downloader_router = Router()


@media_downloader_router.callback_query(MediaEffectsCD.filter())
async def take_media_effect(call: CallbackQuery, callback_data: MediaEffectsCD, bot: Bot, state: FSMContext, lang: str):
    if callback_data.actions == "by_command":
        await state.update_data({"media_effect_type": callback_data.effect})
        await state.set_state(SendMediaSG.send_media)
        await call.message.edit_text("mediani yuboring")
    else:
        load_msg = await call.message.answer("qayta ishlanmoqda")
        media_effect = MediaEffects(message=call.message, bot=bot)
        out_put_media_path = None

        try:
            effect_str = callback_data.effect
            if not effect_str:
                await call.message.answer("Effekt turi topilmadi.")
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
                await call.message.answer("Media topilmadi. Iltimos audio yoki video yuboring.")
                return
            print(effect_str)
            print()
            out_put_media_path = await media_effect.media_effect(
                effect_type=general_effect_type,
                media_type=meida_type,
            )

            print("OUTPUT PATH ->", out_put_media_path)

            if not out_put_media_path or not await asyncio.to_thread(os.path.exists, out_put_media_path):
                await call.message.answer("Media qayta ishlanmadi yoki xatolik yuz berdi.")
                return

            if meida_type == MediaType.VIDEO:
                await call.message.answer_video(
                    FSInputFile(out_put_media_path),
                    caption=media_process_text["downloadin_by"][lang],
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
                        caption=media_process_text["downloadin_by"][lang],
                        title=title_text
                    )
                )
        except Exception as e:
            print("ERROR in take_media:", e)
            await call.message.answer("xatolik yuz berdi")
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
                    print("ERROR", e)

@media_downloader_router.message(SendMediaSG.send_media)
async def take_media(message: Message, state: FSMContext, bot: Bot, lang: str):
    load_msg = await message.answer("qayta ishlanmoqda")
    media_effect = MediaEffects(message=message, bot=bot)

    data = await state.get_data()
    out_put_media_path = None

    try:
        effect_str = data.get("media_effect_type")
        if not effect_str:
            await message.answer("Effekt turi topilmadi.")
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
            await message.answer("Media topilmadi. Iltimos audio yoki video yuboring.")
            return

        out_put_media_path = await media_effect.media_effect(
            effect_type=general_effect_type,
            media_type=meida_type,
        )

        print("OUTPUT PATH ->", out_put_media_path)

        if not out_put_media_path or not await asyncio.to_thread(os.path.exists, out_put_media_path):
            await message.answer("Media qayta ishlanmadi yoki xatolik yuz berdi.")
            return

        if meida_type == MediaType.VIDEO:
            await message.answer_video(
                FSInputFile(out_put_media_path),
                caption=media_process_text["downloadin_by"][lang],
                title="effect video"
            )
        else:
            audio_title = None
            if message.audio and getattr(message.audio, "title", None):
                audio_title = message.audio.title

            effect_name = effect_str or (general_effect_type.value if general_effect_type else "")

            title_text = f"{audio_title} {effect_name} remix" if audio_title else f"voice {effect_name} remix"

            await message.edit_media(
                InputMediaAudio(
                    media=FSInputFile(out_put_media_path),
                    caption=media_process_text["downloadin_by"][lang],
                    title=title_text
                )
            )

    except Exception as e:
        print("ERROR in take_media:", e)
        await message.answer("xatolik yuz berdi")
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
                print("ERROR", e)


@media_downloader_router.message(F.text | F.video | F.video_note | F.voice | F.audio)
async def all_downloader_(message: Message, lang: str):
    for f in [message.audio, message.voice, message.video, message.video_note]:
        if f:
            if f.file_size > 2000 * 1024 * 1024:
                await message.answer(media_process_text["very_big_file"][lang])
                return

    video_path = None
    post_paths = None
    photo_path = None
    thumbnail_path = None
    highlights_path = None
    load_msg = None
    all_downloader = AllDownloader(message=message, lang=lang)

    try:
        if message.text:
            if "https://" in message.text[:8]:
                if "instagram" in message.text:
                    if "https://www.instagram.com/stories/highlights/" in message.text:
                        load_msg = await message.answer(video_process_texts["downloading"][lang])
                        highlights_path = await all_downloader.instagram_downloaders(
                            message.text,
                            InstagramMediaType.HIGHLIGHT
                        )
                        for highlight_path in highlights_path:
                            await message.reply_video(
                                FSInputFile(highlight_path),
                                reply_markup=video_keyboards(
                                    lang
                                ),
                                caption=media_process_text["downloadin_by"][lang]
                            )

                    elif "https://www.instagram.com/stories/" in message.text:
                        load_msg = await message.answer(video_process_texts["downloading"][lang])
                        video_path = await all_downloader.instagram_downloaders(message.text, InstagramMediaType.STORIES)
                        await message.reply_video(
                            FSInputFile(video_path),
                            reply_markup=video_keyboards(
                                lang
                            ),
                            caption=media_process_text["downloadin_by"][lang]
                        )
                    elif "https://www.instagram.com/" in message.text and "p/" in message.text:
                        load_msg = await message.answer(video_process_texts["downloading"][lang])
                        post_paths = await all_downloader.instagram_downloaders(message.text, InstagramMediaType.POST)

                        for post in post_paths:
                            if isinstance(post["path"], str):
                                if "/media/videos/" in post["path"]:
                                    await message.reply_video(
                                        FSInputFile(post["path"]),
                                        caption=media_process_text["downloadin_by"][lang],
                                        reply_markup=video_keyboards(lang)
                                    )
                                elif "/media/photos/" in post["path"]:
                                    await message.reply_photo(
                                        FSInputFile(post["path"]),
                                        caption=media_process_text["downloadin_by"][lang]
                                    )

                            elif isinstance(post["path"], list):
                                media_group = []
                                for i, media in enumerate(post["path"]):
                                    if i == 0:
                                        if "/media/videos/" in media:
                                            media_group.append(
                                                InputMediaVideo(
                                                    media=FSInputFile(media),
                                                    caption=media_process_text["downloadin_by"][lang]
                                                )
                                            )
                                        elif "/media/photos/" in media:
                                            media_group.append(
                                                InputMediaPhoto(
                                                    media=FSInputFile(media),
                                                    caption=media_process_text["downloadin_by"][lang]
                                                )
                                            )
                                    else:
                                        if "/media/videos/" in media:
                                            media_group.append(InputMediaVideo(media=FSInputFile(media)))
                                        else:
                                            media_group.append(InputMediaPhoto(media=FSInputFile(media)))

                                await message.reply_media_group(media=media_group)

                    elif "www.instagram.com" in message.text:
                        load_msg = await message.answer(video_process_texts["downloading"][lang])
                        video_path = await all_downloader.instagram_downloaders(message.text, InstagramMediaType.REELS)
                        await message.reply_video(
                            FSInputFile(video_path),
                            reply_markup=video_keyboards(
                                lang
                            ),
                            caption=media_process_text["downloadin_by"][lang]
                        )
                    else:
                        load_msg = await message.answer(photo_process_texts["downloading"][lang])
                        photo_path = await all_downloader.instagram_downloaders(message.text, InstagramMediaType.PROFILE_PHOTO)
                        await message.reply_photo(
                            FSInputFile(photo_path),
                            caption=media_process_text["downloadin_by"][lang]
                        )

                elif "www.youtube.com" in message.text:
                    url = message.text
                    if "&" in message.text or "&list=" in message.text:
                        url = message.text.split("&")[0]

                    load_msg = await message.answer(video_process_texts["downloading"][lang])
                    video_path = await all_downloader.youtube_downloaders(url)

                    await message.reply_video(
                        FSInputFile(video_path),
                        reply_markup=video_keyboards(
                            lang
                        ),
                        caption=media_process_text["downloadin_by"][lang]
                    )


                elif "www.tiktok.com" in message.text:
                    load_msg = await message.answer(video_process_texts["downloading"][lang])
                    video_path = await all_downloader.tiktok_downloaders(message.text)

                    await message.reply_video(
                        FSInputFile(video_path),
                        reply_markup=video_keyboards(
                            lang
                        ),
                        caption=media_process_text["downloadin_by"][lang]
                    )


                else:
                    await message.answer(video_process_texts["wrong_link"][lang])
            else:
                load_msg = await message.answer(music_and_audio_process_texts["downloading"][lang])
                music_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
                    MusicAction.SEARCH_BY_TEXT
                )
                if music_list:
                    if thumbnail_path:
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
            load_msg = await message.answer(music_and_audio_process_texts["downloading"][lang])
            if message.video:
                music_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
                    MusicAction.SEARCH_BY_MEDIA,
                    MediaType.VIDEO
                )
                if music_list:
                    if thumbnail_path:
                        await message.reply_photo(
                            photo=FSInputFile(thumbnail_path),
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
                    else:
                        await message.reply(
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )

            if message.video_note:
                music_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
                    MusicAction.SEARCH_BY_MEDIA,
                    MediaType.VIDEO_NOTE
                )
                if music_list:
                    if thumbnail_path:
                        await message.reply_photo(
                            photo=FSInputFile(thumbnail_path),
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
                    else:
                        await message.reply(
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
            if message.audio:
                music_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
                    MusicAction.SEARCH_BY_MEDIA,
                    MediaType.AUDIO
                )
                if music_list:
                    if thumbnail_path:
                        await message.reply_photo(
                            photo=FSInputFile(thumbnail_path),
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
                    else:
                        await message.reply(
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
            if message.voice:
                music_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
                    MusicAction.SEARCH_BY_MEDIA,
                    MediaType.VOICE
                )
                if music_list:
                    if thumbnail_path:
                        await message.reply_photo(
                            photo=FSInputFile(thumbnail_path),
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
                    else:
                        await message.reply(
                            text=music_title,
                            reply_markup=music_keyboards(music_list)
                        )
    except Exception as e:
        print("ERROR", e)
        await message.answer(user_texts["error"][lang])
    finally:
        if load_msg:
            await load_msg.delete()

        for path in [video_path, photo_path, thumbnail_path]:
            if path:
                if await asyncio.to_thread(os.path.exists, path):
                    await asyncio.to_thread(os.remove, path)

        if post_paths:
            for post in post_paths:
                if await asyncio.to_thread(os.path.exists, post["path"]):
                    await asyncio.to_thread(os.remove, post["path"])

        if highlights_path:
            for highlight_path in highlights_path:
                if await asyncio.to_thread(os.path.exists, highlight_path):
                    await asyncio.to_thread(os.remove, highlight_path)

@media_downloader_router.callback_query(SearchMusicInVideoCD.filter())
async def send_music_results_from_video(call: CallbackQuery, lang: str):
    load_msg = await call.message.answer(music_and_audio_process_texts["downloading"][lang])
    all_downloader = AllDownloader(call.message)
    thumbnail_path = None
    try:
        musics_list, music_title, thumbnail_path = await all_downloader.music_downloaders(
            actions=MusicAction.SEARCH_BY_MEDIA,
            media_type=MediaType.VIDEO
        )

        if musics_list:
            if thumbnail_path:
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
            await call.message.edit_text(music_and_audio_process_texts["error_in_downloading"][lang])
    except Exception as e:
        print("ERROR", e)
        await call.message.answer(music_and_audio_process_texts["error_in_downloading"][lang])
    finally:
        if await asyncio.to_thread(os.path.exists, thumbnail_path):
            await asyncio.to_thread(os.remove, thumbnail_path)
        if load_msg:
            await load_msg.delete()


@media_downloader_router.callback_query(MusicCD.filter())
async def send_music_search_results(call: CallbackQuery, callback_data: MusicCD, lang: str):
    load_msg = await call.message.answer(music_and_audio_process_texts["downloading"][lang])
    download_music = AllDownloader()
    music_path = None
    print(111111)
    try:
        music_path, title = await download_music.music_downloaders(
            actions=MusicAction.DOWNLOAD,
            some_data=callback_data.video_id
        )
        print(222222)

        await call.message.reply_audio(
            audio=FSInputFile(music_path),
            title=title,
            caption=media_process_text["downloadin_by"][lang],
            reply_markup=audio_keyboard
        )
    except Exception as e:
        print("ERROR", e)
        await call.message.answer(text=music_and_audio_process_texts["error_in_downloading"][lang])
    finally:
        if load_msg:
            await load_msg.delete()
        if music_path:
            if await asyncio.to_thread(os.path.exists, music_path):
                await asyncio.to_thread(os.remove, music_path)


@media_downloader_router.callback_query(AudioCD.filter())
async def send_video_mp3_audio_version(call: CallbackQuery, lang: str, bot: Bot):
    load_msg = await call.message.answer(music_and_audio_process_texts["downloading_audio"][lang])
    downloader_audio = AllDownloader()
    audio_path = None
    video_path = None

    try:
        file = await bot.get_file(call.message.video.file_id)

        file_path = file.file_path
        video_path = f"./media/videos/{get_video_file_name()}"

        await bot.download_file(file_path, video_path)

        audio_path = await downloader_audio.extract_video_to_audio(video_path)

        await call.message.answer_audio(
            FSInputFile(audio_path),
            caption=media_process_text["downloadin_by"][lang],
            title="mp3"
        )

    except Exception as e:
        print("ERROR", e)
        await call.message.answer(text=music_and_audio_process_texts["error_in_downloading_audio"][lang])

    finally:
        if load_msg:
            await load_msg.delete()
        for file in [audio_path, video_path]:
            if file and await asyncio.to_thread(os.path.exists, file):
                await asyncio.to_thread(os.remove, file)


@media_downloader_router.callback_query(F.data == "effects")
async def audio_effects(call: CallbackQuery):
    audio_file_id = call.message.audio.file_id
    await call.message.answer_audio(
        audio_file_id,
        caption="pastdagi efectlardan birini tanlang",
        reply_markup=auido_effect_kbd(
            actions="for_downloading_audio"
        )
    )