from enum import Enum


class DownloadError(Enum):
    FILE_TOO_BIG = "file_is_so_big"
    DOWNLOAD_ERROR = "error_in_downloading"
    MUSIC_NOT_FOUND = "music_not_found"
    INVALID_MEDIA_TYPE = "invalid_media_type"
