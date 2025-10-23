from enum import Enum


class MusicAction(Enum):
    SEARCH_BY_TEXT = "search_music_by_text_or_avtro_name"
    DOWNLOAD = "download_music"
    SEARCH_BY_MEDIA = "search_music_by_media"


class AudioEffectAction(Enum):
    EFFECT_8D = "8d"
    EFFECT_SLOWED = "slowed"
    EFFECT_SPEED = "speed"
    EFFECT_CONCERT_HALL = "concert_hall"