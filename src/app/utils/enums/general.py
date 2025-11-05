from enum import Enum


class GeneralEffectAction(Enum):
    EFFECT_8D = "8d"
    EFFECT_SLOWED = "slowed"
    EFFECT_SPEED = "speed"
    EFFECT_CONCERT_HALL = "concert hall"


class MediaType(Enum):
    VIDEO_NOTE = "video_note"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    PHOTO = "photo"