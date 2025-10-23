import time


def get_video_file_name() -> str:
    file_name = time.time_ns()
    return f"{file_name}.mp4"

def get_audio_file_name() -> str:
    file_name = time.time_ns()
    return f"{file_name}.mp3"

def get_photo_file_name() -> str:
    file_name = time.time_ns()
    return f"{file_name}.jpg"