import asyncio
import os
import subprocess

from faster_whisper import WhisperModel
from pydub import AudioSegment

from src.app.services.media_downloaders.utils.files import get_audio_file_name


class AudioUtils:
    def __init__(self):
        self.subprocess = subprocess

    def extract_audio_from_video(self, video_path: str, audio_path: str) -> bool:

        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-vn",
                "-acodec", "mp3",
                audio_path
            ]

            self.subprocess.run(cmd, check=True, capture_output=True, text=True)
            return os.path.exists(audio_path)

        except subprocess.CalledProcessError as e:
            print(f"[AudioUtils] FFmpeg error: {e.stderr}")
        except Exception as e:
            print(f"[AudioUtils] extract_audio_from_video error: {e}")
        return False

    def convert_audio(self, input_file: str) -> str:
        audio = AudioSegment.from_file(input_file)
        wav_file = f"./media/audios/{get_audio_file_name()}.wav"
        audio.export(wav_file, format="wav")
        return wav_file

    async def speech_to_text(self, file_path: str, language: str = "uz") -> str:
        file_waw = None
        try:
            model = WhisperModel("tiny", device="cpu", compute_type="int8")

            if not file_path.endswith(".wav"):
                file_waw = await asyncio.to_thread(self.convert_audio, file_path)

            segments, info = await asyncio.to_thread(
                model.transcribe, file_waw, language=language
            )
            text = ""
            for segment in segments:
                text += segment.text
                break

            return text



        except Exception as e:
            print("ERROR", e)
        finally:
            if await asyncio.to_thread(os.path.exists, file_waw):
                await asyncio.to_thread(os.remove, file_waw)



