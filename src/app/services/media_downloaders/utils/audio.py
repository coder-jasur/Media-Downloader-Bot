import asyncio
import os
import subprocess
from typing import Optional

from pedalboard import Pedalboard
from pedalboard_native import HighpassFilter, LowpassFilter, Reverb, Compressor
from pedalboard_native.io import AudioFile

from src.app.services.media_downloaders.utils.files import get_audio_file_name
from src.app.utils.enums.audio import AudioEffectAction


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

    # def apply_effect(self, input_file: str, output_file: str, effect_type: str, media_type: str) -> Optional[str]:
    #
    #     effects = {
    #         "concert": "aecho=0.5:0.6:1100:0.2, lowpass=f=3000, highpass=f=150, pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c1+0.5*c0, volume=0.90",
    #         "8d": "apulsator=hz=0.2",
    #         "slowed": "atempo=0.85",
    #         "speed": "atempo=1.25"
    #     }
    #
    #     if effect_type not in effects:
    #         print(f"[AudioUtils] Unknown effect type: {effect_type}")
    #         return None
    #
    #     try:
    #         if media_type == "audio":
    #             cmd = [
    #                 "ffmpeg", "-y",
    #                 "-i", input_file,
    #                 "-filter_complex", effects[effect_type],
    #                 "-c:a", "libmp3lame",  # ✅ MP3 uchun to‘g‘ri kodek
    #                 "-b:a", "320k",  # ✅ eng yuqori sifat
    #                 output_file
    #             ]
    #
    #         elif media_type == "video":
    #             if effect_type in ["concert", "8d"]:
    #                 cmd = [
    #                     "ffmpeg", "-y",
    #                     "-i", input_file,
    #                     "-c:v", "copy",
    #                     "-filter:a", effects[effect_type],
    #                     "-c:a", "aac", "-b:a", "320k",
    #                     output_file
    #                 ]
    #             elif effect_type in ["slowed", "speed"]:
    #                 atempo_val = 0.85 if effect_type == "slowed" else 1.25
    #                 setpts_val = 1 / atempo_val
    #
    #                 filter_complex = f"[0:v]setpts={setpts_val:.3f}*PTS[v];[0:a]atempo={atempo_val:.3f}[a]"
    #
    #                 cmd = [
    #                     "ffmpeg", "-y",
    #                     "-i", input_file,
    #                     "-filter_complex", filter_complex,
    #                     "-map", "[v]", "-map", "[a]",
    #                     "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    #                     "-c:a", "aac", "-b:a", "320k",
    #                     output_file
    #                 ]
    #             else:
    #                 print(f"[AudioUtils] Unsupported video effect: {effect_type}")
    #                 return None
    #         else:
    #             print(f"[AudioUtils] Invalid media_type: {media_type}")
    #             return None
    #
    #         result = self.subprocess.run(cmd, capture_output=True, text=True)
    #         if result.returncode != 0:
    #             print(f"[AudioUtils] FFmpeg error: {result.stderr}")
    #             return None
    #
    #         return output_file
    #
    #     except Exception as e:
    #         print(f"[AudioUtils] apply_effect error: {e}")
    #         return None

class MediaEffects:
    def __init__(self):
        self.subprocess = asyncio.subprocess


    async def audio_effects(self, input_file: str, effect_type: AudioEffectAction):

        output_file_path = f"./media/audios/{effect_type}_{get_audio_file_name()}"

        if effect_type == effect_type.EFFECT_SLOWED:
            cmd = [
                "ffmpeg", "-y", "-i", input_file,
                "-filter_complex", "[0:a]asetrate=44100*0.85,aresample=44100,atempo=1.0,volume=1.05[a]",
                "-map", "[a]", output_file_path
            ]
            process = await asyncio.create_subprocess_exec(*cmd)
            await process.wait()
            return output_file_path
        elif effect_type in [effect_type.EFFECT_SPEED, effect_type.EFFECT_8D]:
            effects = {
                "8d": "apulsator=hz=0.2",
                "speed": "atempo=1.25"
            }
            cmd = [
                "ffmpeg", "-y",
                "-i", input_file,
                "-filter_complex", effects[effect_type],
                "-c:a", "libmp3lame",
                "-b:a", "320k",
                output_file_path
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=self.subprocess.PIPE,
                stderr=self.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                print(f"[AudioUtils] FFmpeg error: {stderr.decode()}")
                return None

            return output_file_path
        elif effect_type == effect_type.EFFECT_CONCERT_HALL:
            temp_wav = "temp.wav"

            ffmpeg_cmd = ["ffmpeg", "-y", "-i", input_file, temp_wav]
            process = await asyncio.create_subprocess_exec(*ffmpeg_cmd)
            await process.wait()

            def process_audio():
                with AudioFile(temp_wav) as f:
                    audio = f.read(f.frames)
                    samplerate = f.samplerate

                board = Pedalboard([
                        HighpassFilter(cutoff_frequency_hz=180),
                        LowpassFilter(cutoff_frequency_hz=9000),
                        Reverb(room_size=0.82, wet_level=0.55, dry_level=0.5, width=1.0),
                        Compressor(threshold_db=-12, ratio=2.5),
                    ])

                effected = board(audio, samplerate)
                with AudioFile(output_file_path, "w", samplerate, effected.shape[0]) as f:
                    f.write(effected)
                return output_file_path

            result = await asyncio.to_thread(process_audio)
            return result