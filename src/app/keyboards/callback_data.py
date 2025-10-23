from aiogram.filters.callback_data import CallbackData


class MusicCD(CallbackData, prefix="music"):
    video_id: str


class SearchMusicInVideoCD(CallbackData, prefix="search_music"):
    action: str

class AudioCD(CallbackData, prefix="audio"):
    action: str

class AudioEffectCD(CallbackData, prefix="audio_effect"):
    effect: str