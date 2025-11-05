from aiogram.filters.callback_data import CallbackData

from src.app.database.queries.channels import ChannelDataBaseActions
from src.app.utils.enums.actions import AdminMenuActions, BotActions, ChannelActions, AddMandatorySubscriptionActions, \
    ReferalsActions
from src.app.utils.enums.general import GeneralEffectAction


class MusicCD(CallbackData, prefix="music"):
    video_id: str

class TopPopularMusicCD(CallbackData, prefix="popular_musics"):
    music_name: str

class SearchMusicInVideoCD(CallbackData, prefix="search_music"):
    action: str

class AudioCD(CallbackData, prefix="audio"):
    action: str

class MediaEffectsCD(CallbackData, prefix="media_effect"):
    actions: str
    effect: GeneralEffectAction

class AdminMainMenuCD(CallbackData, prefix="admin_mani_menu"):
    actions: AdminMenuActions


class ChannelCD(CallbackData, prefix="channel"):
    id: int
    action: ChannelActions

class BotCD(CallbackData, prefix="bot"):
    username: str
    action: BotActions

class ReferralCD(CallbackData, prefix="referral"):
    referral_id: str
    action: ReferalsActions

class AddMandatorySubscriptionCD(CallbackData, prefix="mandatory_subscription"):
    actions: AddMandatorySubscriptionActions
