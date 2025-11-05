from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict


class URLType(str, Enum):
    """All possible URL types"""
    # Unknown
    UNKNOWN = "unknown"

    # Instagram
    INSTAGRAM_POST = "instagram_post"
    INSTAGRAM_REEL = "instagram_reel"
    INSTAGRAM_STORIES = "instagram_stories"
    INSTAGRAM_IGTV = "instagram_igtv"
    INSTAGRAM_HIGHLIGHT = "instagram_highlight"
    INSTAGRAM_LIVE = "instagram_live"
    INSTAGRAM_PROFILE_PHOTO = "instagram_profile"
    INSTAGRAM_CDN_VIDEO = "instagram_cdn_video"
    INSTAGRAM_CDN_PHOTO = "instagram_cdn_photo"
    INSTAGRAM_CDN_UNKNOWN = "instagram_cdn_unknown"

    # YouTube
    YOUTUBE_VIDEO = "youtube_video"
    YOUTUBE_SHORTS = "youtube_shorts"
    YOUTUBE_LIVE = "youtube_live"
    YOUTUBE_PLAYLIST = "youtube_playlist"
    YOUTUBE_CDN_VIDEO = "youtube_cdn_video"
    YOUTUBE_CDN_PHOTO = "youtube_cdn_photo"
    YOUTUBE_CDN_UNKNOWN = "youtube_cdn_unknown"

    # TikTok
    TIKTOK_VIDEO = "tiktok_video"
    TIKTOK_PHOTO = "tiktok_photo"
    TIKTOK_LIVE = "tiktok_live"
    TIKTOK_PROFILE = "tiktok_profile"
    TIKTOK_CDN_VIDEO = "tiktok_cdn_video"
    TIKTOK_CDN_PHOTO = "tiktok_cdn_photo"
    TIKTOK_CDN_UNKNOWN = "tiktok_cdn_unknown"

@dataclass
class URLInfo:
    """Information about validated URL"""
    url_type: URLType
    platform: str  # "instagram", "youtube", "tiktok", etc.
    is_cdn: bool
    video_id: Optional[str] = None
    username: Optional[str] = None
    clean_url: Optional[str] = None
    metadata: Optional[Dict] = None