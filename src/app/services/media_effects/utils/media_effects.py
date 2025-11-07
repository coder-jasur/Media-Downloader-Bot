import asyncio
import os

from pedalboard import Pedalboard
from pedalboard_native import HighpassFilter, Reverb, LowpassFilter, Compressor
from pedalboard_native.io import AudioFile

from src.app.utils.enums.general import GeneralEffectAction


class MediaEffectsTools:
    async def audio_effects(self, input_file: str, effect_type: GeneralEffectAction):
        try:
            base, _ = await asyncio.to_thread(os.path.splitext, input_file)
            temp_wav = f"{base}_temp.wav"
            processed_wav = f"{base}_processed.wav"
            output_file_path = f"{base}_effected.mp3"

            # Input faylni WAV ga o'zgartirish
            ffmpeg_cmd = ["ffmpeg", "-y", "-i", input_file, "-ac", "2", "-ar", "44100", temp_wav]
            p = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
            await p.wait()

            if not await asyncio.to_thread(os.path.exists, temp_wav):
                raise FileNotFoundError("Failed to convert input to WAV")

            # 8D effekti
            if effect_type == GeneralEffectAction.EFFECT_8D:
                ff_cmd = ["ffmpeg", "-y", "-i", temp_wav, "-filter_complex", "apulsator=hz=0.2", "-ac", "2", processed_wav]
                p2 = await asyncio.create_subprocess_exec(*ff_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await p2.communicate()
                if p2.returncode != 0:
                    print("[AudioEffects] FFmpeg 8D error:", stderr.decode(errors="ignore"))
                    raise RuntimeError("FFmpeg failed to produce 8D effect")

            # Sezilgan sekinlashtirish
            elif effect_type == GeneralEffectAction.EFFECT_SLOWED:
                ff_slow = [
                    "ffmpeg", "-y", "-i", input_file,
                    "-filter_complex", "[0:a]asetrate=44100*0.85,aresample=44100,atempo=1.0,volume=1.05[a]",
                    "-map", "[a]", processed_wav
                ]
                p3 = await asyncio.create_subprocess_exec(*ff_slow, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                await p3.wait()

            # Tezlashtirish
            elif effect_type == GeneralEffectAction.EFFECT_SPEED:
                ff_speed = [
                    "ffmpeg", "-y", "-i", input_file,
                    "-filter_complex", "[0:a]asetrate=44100*1.25,aresample=44100,atempo=1.0,volume=1.05[a]",
                    "-map", "[a]", processed_wav
                ]
                p4 = await asyncio.create_subprocess_exec(*ff_speed, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                await p4.wait()

            # Konsert zal effekti
            elif effect_type == GeneralEffectAction.EFFECT_CONCERT_HALL:
                async def process_audio():
                    def inner():
                        with AudioFile(temp_wav) as f:
                            audio = f.read(f.frames)
                            samplerate = f.samplerate
                        board = Pedalboard([
                            HighpassFilter(cutoff_frequency_hz=180),
                            LowpassFilter(cutoff_frequency_hz=9000),
                            Reverb(room_size=0.78, wet_level=0.30, dry_level=0.5, width=1.0),
                            Compressor(threshold_db=-18, ratio=2.0),
                        ])
                        effected = board(audio, samplerate)
                        with AudioFile(processed_wav, "w", samplerate, effected.shape[0]) as outf:
                            outf.write(effected)
                    return await asyncio.to_thread(inner)

                await process_audio()

            else:
                raise ValueError(f"Unknown effect type: {effect_type}")

            # WAV ni MP3 ga aylantirish
            if await asyncio.to_thread(os.path.exists, processed_wav):
                ff_to_mp3 = ["ffmpeg", "-y", "-i", processed_wav, "-codec:a", "libmp3lame", "-b:a", "320k", output_file_path]
                p5 = await asyncio.create_subprocess_exec(*ff_to_mp3, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
                await p5.wait()
            else:
                raise FileNotFoundError("Processed WAV not found after effect")

            # Vaqtinchalik fayllarni tozalash
            for f in (temp_wav, processed_wav):
                if await asyncio.to_thread(os.path.exists, f):
                    await asyncio.to_thread(os.remove, f)

            if await asyncio.to_thread(os.path.exists, output_file_path):
                return output_file_path
            else:
                raise FileNotFoundError("Output not created")

        except Exception as e:
            print("ERROR audio_effects:", e)
            return None

    async def video_effects(self, input_file: str, effect_type: GeneralEffectAction):
        base, _ = await asyncio.to_thread(os.path.splitext, input_file)
        temp_wav = f"{base}_temp.wav"
        processed_wav = f"{base}_processed.wav"
        output_file_path = f"{base}_effected.mp4"
        try:
            ffmpeg_cmd = ["ffmpeg", "-y", "-i", input_file, "-ac", "2", "-ar", "44100", temp_wav]
            p = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
            await p.wait()

            if not await asyncio.to_thread(os.path.exists, temp_wav):
                raise FileNotFoundError("Failed to convert input to WAV")

            # FFmpeg audio effekti video bilan birlashtiriladi
            if effect_type == GeneralEffectAction.EFFECT_8D:
                cmd = ["ffmpeg", "-y", "-i", input_file, "-c:v", "copy", "-filter:a", "apulsator=hz=0.2", "-c:a", "aac", "-b:a", "320k", output_file_path]
                p = await asyncio.create_subprocess_exec(*cmd)
                await p.wait()
                return output_file_path

            elif effect_type == GeneralEffectAction.EFFECT_SLOWED:
                cmd = ["ffmpeg", "-y", "-i", input_file, "-filter_complex", "[0:v]setpts=1.25*PTS[v];[0:a]atempo=0.8[a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "320k", output_file_path]
                p = await asyncio.create_subprocess_exec(*cmd)
                await p.wait()
                return output_file_path

            elif effect_type == GeneralEffectAction.EFFECT_SPEED:
                cmd = ["ffmpeg", "-y", "-i", input_file, "-filter_complex", "[0:v]setpts=0.75*PTS[v];[0:a]atempo=1.25[a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", "-b:a", "320k", output_file_path]
                p = await asyncio.create_subprocess_exec(*cmd)
                await p.wait()
                return output_file_path

            elif effect_type == GeneralEffectAction.EFFECT_CONCERT_HALL:
                async def process_audio():
                    def inner():
                        with AudioFile(temp_wav) as f:
                            audio = f.read(f.frames)
                            samplerate = f.samplerate
                        board = Pedalboard([
                            HighpassFilter(cutoff_frequency_hz=180),
                            LowpassFilter(cutoff_frequency_hz=9000),
                            Reverb(room_size=0.78, wet_level=0.30, dry_level=0.5, width=1.0),
                            Compressor(threshold_db=-18, ratio=2.0),
                        ])
                        effected = board(audio, samplerate)
                        with AudioFile(processed_wav, "w", samplerate, effected.shape[0]) as outf:
                            outf.write(effected)
                    return await asyncio.to_thread(inner)

                await process_audio()

                cmd = ["ffmpeg", "-y", "-i", input_file, "-i", processed_wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", output_file_path]
                p = await asyncio.create_subprocess_exec(*cmd)
                await p.wait()
                return output_file_path

            else:
                return input_file

        except Exception as e:
            print("ERROR in video_effects:", e)
            return None

        finally:
            for f in (temp_wav, processed_wav):
                if await asyncio.to_thread(os.path.exists, f):
                    await asyncio.to_thread(os.remove, f)
