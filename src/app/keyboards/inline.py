from aiogram.types import InlineKeyboardButton, MessageOrigin, Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.app.keyboards.callback_data import MusicCD, SearchMusicInVideoCD, AudioCD, AudioEffectCD
from src.app.texts import admin_menu_texts, music_and_audio_process_texts


def video_keyboards(lang: str):
    buttons = InlineKeyboardBuilder()
    buttons.row(
        InlineKeyboardButton(
            text=music_and_audio_process_texts["download_is"][lang],
            callback_data=SearchMusicInVideoCD(
                action="search_music",
            ).pack()
        )
    )
    buttons.row(
        InlineKeyboardButton(
            text="🔊 mp3",
            callback_data=AudioCD(
                action="download_audio"
            ).pack()
        )
    )
    return buttons.as_markup()


def music_keyboards(music_list: list):
    builder = InlineKeyboardBuilder()
    i = 1

    for music in music_list:
        builder.add(
            InlineKeyboardButton(
                text=str(i),
                callback_data=MusicCD(video_id=music["id"]).pack()
            )
        )
        i += 1

    builder.adjust(5)

    builder.row(
        InlineKeyboardButton(
            text="❌",
            callback_data="delete_list_music"
        )
    )

    return builder.as_markup()


def back_to_subscriptions_menu_button(lang: str):
    buttons = InlineKeyboardBuilder()

    buttons.row(
        InlineKeyboardButton(
            text=admin_menu_texts["back_button"][lang],
            callback_data="back_to_subscriptions_menu"
        )
    )
    return buttons.as_markup()


auido_effect = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🎤 Konsert", callback_data=AudioEffectCD(effect="concert").pack()),
            InlineKeyboardButton(text="🌀 8D", callback_data=AudioEffectCD(effect="8d").pack())
        ],
        [
            InlineKeyboardButton(text="🐢 Slowed", callback_data=AudioEffectCD(effect="slowed").pack()),
            InlineKeyboardButton(text="⚡ Speed", callback_data=AudioEffectCD(effect="speed").pack())
        ]
    ]
)
