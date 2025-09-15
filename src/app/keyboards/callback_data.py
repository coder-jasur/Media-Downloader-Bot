from aiogram.filters.callback_data import CallbackData


class MusicCD(CallbackData, prefix="music"):
    video_id: str


class VideoMusicCD(CallbackData, prefix="videomusic"):
    music_name: str

