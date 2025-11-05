import re
from urllib.parse import urlparse, parse_qs, unquote

from src.app.utils.enums.url import URLType, URLInfo


# ==================== VALIDATOR CLASS ====================

class SocialMediaURLValidator:
    """
    Professional URL validator for social media platforms
    """

    # Domain patterns
    INSTAGRAM_DOMAINS = {
        "instagram.com", "instagr.am",
        "cdninstagram.com", "fbcdn.net"
    }

    YOUTUBE_DOMAINS = {
        "youtube.com", "youtu.be", "m.youtube.com",
        "ytimg.com", "googlevideo.com", "yt.be"
    }

    TIKTOK_DOMAINS = {
        "tiktok.com", "vt.tiktok.com", "vm.tiktok.com",
        "tiktokcdn.com", "tiktokv.com", "tiktokapi.com",
        "p16-sign-va.tiktokcdn.com"
    }


    @staticmethod
    def _clean_url(url: str) -> str:
        """Clean and normalize URL"""
        if not url:
            return ""

        url = url.strip()

        # Decode URL encoding
        url = unquote(url)

        # Add https if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        return url

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. and mobile. prefixes
            domain = re.sub(r"^(www\.|m\.|mobile\.)", "", domain)
            return domain
        except Exception as e:
            print("ERROR", e)
            return ""

    @staticmethod
    def _is_cdn_domain(domain: str, cdn_keywords: tuple) -> bool:
        """Check if domain is CDN"""
        return any(keyword in domain for keyword in cdn_keywords)

    @staticmethod
    def _get_file_type(url: str) -> str:
        """Determine file type from URL"""
        url_lower = url.lower()

        # Video extensions
        video_exts = (".mp4", ".mov", ".avi", ".webm", ".m4a", ".mkv")
        if any(url_lower.endswith(ext) for ext in video_exts):
            return "video"

        # Photo extensions
        photo_exts = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp")
        if any(url_lower.endswith(ext) for ext in photo_exts):
            return "photo"

        return "unknown"

    # ==================== INSTAGRAM ====================

    def _validate_instagram(self, url: str, domain: str) -> URLInfo:

        """Validate Instagram URL"""
        url_lower = url.lower()

        # Check if CDN
        if self._is_cdn_domain(domain, ("cdninstagram", "fbcdn")):
            file_type = self._get_file_type(url)

            # ✅ Profil rasmlari uchun alohida aniqlash
            if "t51.2885-19" in url:
                return URLInfo(
                    url_type=URLType.INSTAGRAM_PROFILE_PHOTO,
                    platform="instagram",
                    is_cdn=True,
                    clean_url=url
                )

            if file_type == "video":
                return URLInfo(
                    url_type=URLType.INSTAGRAM_CDN_VIDEO,
                    platform="instagram",
                    is_cdn=True,
                    clean_url=url
                )
            elif file_type == "photo":
                return URLInfo(
                    url_type=URLType.INSTAGRAM_CDN_PHOTO,
                    platform="instagram",
                    is_cdn=True,
                    clean_url=url
                )
            else:
                return URLInfo(
                    url_type=URLType.INSTAGRAM_CDN_UNKNOWN,
                    platform="instagram",
                    is_cdn=True,
                    clean_url=url
                )

        # Regular Instagram URLs
        # Post: /p/CODE/
        if re.search(r"/p/[\w-]+", url_lower):
            post_id = re.search(r"/p/([\w-]+)", url_lower)
            return URLInfo(
                url_type=URLType.INSTAGRAM_POST,
                platform="instagram",
                is_cdn=False,
                video_id=post_id.group(1) if post_id else None,
                clean_url=url
            )

        # Reel: /reel/CODE/ or /reels/CODE/
        if re.search(r"/reels?/[\w-]+", url_lower):
            reel_id = re.search(r"/reels?/([\w-]+)", url_lower)
            return URLInfo(
                url_type=URLType.INSTAGRAM_REEL,
                platform="instagram",
                is_cdn=False,
                video_id=reel_id.group(1) if reel_id else None,
                clean_url=url
            )

        # Highlights: /stories/highlights/ID/ (CHECK THIS FIRST!)
        if "/stories/highlights/" in url_lower or "/highlights/" in url_lower:
            highlight_id = re.search(r"/(?:stories/)?highlights?/([\w-]+)", url_lower)
            return URLInfo(
                url_type=URLType.INSTAGRAM_HIGHLIGHT,
                platform="instagram",
                is_cdn=False,
                video_id=highlight_id.group(1) if highlight_id else None,
                clean_url=url
            )

        # Stories: /stories/USERNAME/ID/ (AFTER highlights check!)
        if "/stories/" in url_lower:
            story_match = re.search(r"/stories/([\w.]+)/(\d+)", url_lower)
            return URLInfo(
                url_type=URLType.INSTAGRAM_STORIES,
                platform="instagram",
                is_cdn=False,
                username=story_match.group(1) if story_match else None,
                video_id=story_match.group(2) if story_match else None,
                clean_url=url
            )

        # IGTV: /tv/CODE/
        if "/tv/" in url_lower:
            tv_id = re.search(r"/tv/([\w-]+)", url, re.IGNORECASE)
            return URLInfo(
                url_type=URLType.INSTAGRAM_IGTV,
                platform="instagram",
                is_cdn=False,
                video_id=tv_id.group(1) if tv_id else None,
                clean_url=url
            )

        # Highlights: /highlights/ID/ (WITHOUT /stories/ prefix)
        if "/highlights/" in url_lower:
            highlight_id = re.search(r"/highlights?/([\w-]+)", url, re.IGNORECASE)
            return URLInfo(
                url_type=URLType.INSTAGRAM_HIGHLIGHT,
                platform="instagram",
                is_cdn=False,
                video_id=highlight_id.group(1) if highlight_id else None,
                clean_url=url
            )

        # Live: /live/USERNAME/
        if "/live/" in url_lower:
            return URLInfo(
                url_type=URLType.INSTAGRAM_LIVE,
                platform="instagram",
                is_cdn=False,
                clean_url=url
            )

        # Profile: /USERNAME/
        profile_match = re.match(
            r"^https?://(?:www\.)?instagram\.com/([\w.]+)/?$",
            url_lower
        )
        if profile_match:
            return URLInfo(
                url_type=URLType.INSTAGRAM_PROFILE_PHOTO,
                platform="instagram",
                is_cdn=False,
                username=profile_match.group(1),
                clean_url=url
            )

        return URLInfo(
            url_type=URLType.UNKNOWN,
            platform="instagram",
            is_cdn=False,
            clean_url=url
        )

    # ==================== YOUTUBE ====================

    def _validate_youtube(self, url: str, domain: str) -> URLInfo:
        """Validate YouTube URL"""
        url_lower = url.lower()

        # Check if CDN
        if self._is_cdn_domain(domain, ("ytimg", "googlevideo")):
            file_type = self._get_file_type(url)

            if file_type == "video":
                return URLInfo(
                    url_type=URLType.YOUTUBE_CDN_VIDEO,
                    platform="youtube",
                    is_cdn=True,
                    clean_url=url
                )
            elif file_type == "photo":
                return URLInfo(
                    url_type=URLType.YOUTUBE_CDN_PHOTO,
                    platform="youtube",
                    is_cdn=True,
                    clean_url=url
                )
            else:
                return URLInfo(
                    url_type=URLType.YOUTUBE_CDN_UNKNOWN,
                    platform="youtube",
                    is_cdn=True,
                    clean_url=url
                )

        # Shorts: /shorts/VIDEO_ID
        if "/shorts/" in url_lower:
            # Use original URL to preserve case
            video_id = re.search(r"/shorts/([\w-]+)", url, re.IGNORECASE)
            return URLInfo(
                url_type=URLType.YOUTUBE_SHORTS,
                platform="youtube",
                is_cdn=False,
                video_id=video_id.group(1) if video_id else None,
                clean_url=url
            )

        # Regular video: v=VIDEO_ID or youtu.be/VIDEO_ID
        video_id = None

        # youtu.be format
        if "youtu.be" in domain:
            # Use original URL to preserve case-sensitive video ID
            match = re.search(r"youtu\.be/([\w-]+)", url, re.IGNORECASE)
            if match:
                video_id = match.group(1)

        # youtube.com format
        else:
            # From query parameter (use ORIGINAL url, not lowercased!)
            parsed = urlparse(url)  # Don't use url_lower here!
            params = parse_qs(parsed.query)
            if "v" in params and params["v"][0]:  # Check if not empty!
                video_id = params["v"][0]

            # From path
            if not video_id:
                # Use original URL to preserve case
                match = re.search(r"[?&]v=([\w-]+)", url, re.IGNORECASE)
                if match:
                    video_id = match.group(1)

        if video_id:
            return URLInfo(
                url_type=URLType.YOUTUBE_VIDEO,
                platform="youtube",
                is_cdn=False,
                video_id=video_id,
                clean_url=f"https://www.youtube.com/watch?v={video_id}"
            )

        # Live: /live/VIDEO_ID
        if "/live/" in url_lower:
            live_id = re.search(r"/live/([\w-]+)", url, re.IGNORECASE)
            return URLInfo(
                url_type=URLType.YOUTUBE_LIVE,
                platform="youtube",
                is_cdn=False,
                video_id=live_id.group(1) if live_id else None,
                clean_url=url
            )

        # Playlist: list=PLAYLIST_ID
        if "list=" in url_lower:
            # Use original URL for parameters
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            playlist_id = params.get("list", [None])[0]
            return URLInfo(
                url_type=URLType.YOUTUBE_PLAYLIST,
                platform="youtube",
                is_cdn=False,
                video_id=playlist_id,
                clean_url=url
            )

        return URLInfo(
            url_type=URLType.UNKNOWN,
            platform="youtube",
            is_cdn=False,
            clean_url=url
        )

    # ==================== TIKTOK ====================

    def _validate_tiktok(self, url: str, domain: str) -> URLInfo:
        """Validate TikTok URL"""
        url_lower = url.lower()

        # Check if CDN
        if self._is_cdn_domain(domain, ("tiktokcdn", "tiktokv", "tiktokapi")):
            file_type = self._get_file_type(url)

            if file_type == "video":
                return URLInfo(
                    url_type=URLType.TIKTOK_CDN_VIDEO,
                    platform="tiktok",
                    is_cdn=True,
                    clean_url=url
                )
            elif file_type == "photo":
                return URLInfo(
                    url_type=URLType.TIKTOK_CDN_PHOTO,
                    platform="tiktok",
                    is_cdn=True,
                    clean_url=url
                )
            else:
                return URLInfo(
                    url_type=URLType.TIKTOK_CDN_UNKNOWN,
                    platform="tiktok",
                    is_cdn=True,
                    clean_url=url
                )

        # Video: /@USERNAME/video/ID or /video/ID
        if "/video/" in url_lower:
            video_match = re.search(r"/@([\w.]+)/video/(\d+)", url_lower)
            if video_match:
                return URLInfo(
                    url_type=URLType.TIKTOK_VIDEO,
                    platform="tiktok",
                    is_cdn=False,
                    username=video_match.group(1),
                    video_id=video_match.group(2),
                    clean_url=url
                )

            # Just /video/ID
            video_id = re.search(r"/video/(\d+)", url_lower)
            return URLInfo(
                url_type=URLType.TIKTOK_VIDEO,
                platform="tiktok",
                is_cdn=False,
                video_id=video_id.group(1) if video_id else None,
                clean_url=url
            )

        # Photo: /@USERNAME/photo/ID
        if "/photo/" in url_lower:
            photo_match = re.search(r"/@([\w.]+)/photo/(\d+)", url_lower)
            return URLInfo(
                url_type=URLType.TIKTOK_PHOTO,
                platform="tiktok",
                is_cdn=False,
                username=photo_match.group(1) if photo_match else None,
                video_id=photo_match.group(2) if photo_match else None,
                clean_url=url
            )

        # Live: /@USERNAME/live
        if re.search(r"/@[\w.]+/live", url_lower):
            username_match = re.search(r"/@([\w.]+)/live", url_lower)
            return URLInfo(
                url_type=URLType.TIKTOK_LIVE,
                platform="tiktok",
                is_cdn=False,
                username=username_match.group(1) if username_match else None,
                clean_url=url
            )

        # Profile: /@USERNAME
        profile_match = re.search(r"/@([\w.]+)/?$", url_lower)
        if profile_match:
            return URLInfo(
                url_type=URLType.TIKTOK_PROFILE,
                platform="tiktok",
                is_cdn=False,
                username=profile_match.group(1),
                clean_url=url
            )

        # Short link: vt.tiktok.com/CODE or vm.tiktok.com/CODE
        if domain in ("vt.tiktok.com", "vm.tiktok.com"):
            return URLInfo(
                url_type=URLType.TIKTOK_VIDEO,
                platform="tiktok",
                is_cdn=False,
                clean_url=url,
                metadata={"short_link": True}
            )

        return URLInfo(
            url_type=URLType.UNKNOWN,
            platform="tiktok",
            is_cdn=False,
            clean_url=url
        )

    # ==================== MAIN VALIDATION ====================

    def validate(self, url: str) -> URLInfo:
        """
        Validate social media URL and return detailed info

        Args:
            url: URL to validate

        Returns:
            URLInfo with platform, type, and metadata
        """
        if not url or not isinstance(url, str):
            return URLInfo(
                url_type=URLType.UNKNOWN,
                platform="unknown",
                is_cdn=False
            )

        # Clean URL
        clean_url = self._clean_url(url)
        domain = self._extract_domain(clean_url)

        if not domain:
            return URLInfo(
                url_type=URLType.UNKNOWN,
                platform="unknown",
                is_cdn=False
            )

        # Route to platform validator
        if any(d in domain for d in self.INSTAGRAM_DOMAINS):
            return self._validate_instagram(clean_url, domain)

        elif any(d in domain for d in self.YOUTUBE_DOMAINS):
            return self._validate_youtube(clean_url, domain)

        elif any(d in domain for d in self.TIKTOK_DOMAINS):
            return self._validate_tiktok(clean_url, domain)

        # Unknown platform
        return URLInfo(
            url_type=URLType.UNKNOWN,
            platform="unknown",
            is_cdn=False,
            clean_url=clean_url
        )

    def validate_simple(self, url: str) -> str:
        """
        Simple validation - returns just the URL type string
        Compatible with old validator_urls function

        Args:
            url: URL to validate

        Returns:
            String like "youtube_video", "instagram_post", etc.
        """
        result = self.validate(url)
        return result.url_type.value



