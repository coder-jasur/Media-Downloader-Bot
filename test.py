import asyncio
import subprocess
from pedalboard import Pedalboard, Reverb, HighpassFilter, LowpassFilter, Compressor
from pedalboard.io import AudioFile

async def add_concert_effect(input_mp3: str, output_wav: str = "concert_hall.wav"):
    """MP3 faylga konsert zal effektini tiniqroq ovoz bilan qo‘shadi."""
    temp_wav = "temp.wav"

    # MP3 → WAV konvertatsiya
    ffmpeg_cmd = ["ffmpeg", "-y", "-i", input_mp3, temp_wav]
    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd)
    await process.wait()

    # Effektlar
    def process_audio():
        with AudioFile(temp_wav) as f:
            audio = f.read(f.frames)
            samplerate = f.samplerate

        board = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=180),     # past tovushlarni yumshatadi
            LowpassFilter(cutoff_frequency_hz=9000),     # yuqori chastotalarni tiniq qiladi
            Reverb(room_size=0.82, wet_level=0.55, dry_level=0.5, width=1.0),  # tabiiy zal effekti
            Compressor(threshold_db=-12, ratio=2.5),     # ovozni barqaror, tiniq qiladi
        ])

        effected = board(audio, samplerate)
        with AudioFile(output_wav, "w", samplerate, effected.shape[0]) as f:
            f.write(effected)
        return output_wav

    result = await asyncio.to_thread(process_audio)
    return result


# Test
async def main():
    file = await add_concert_effect("input.mp3")
    print("✅ Effekt tayyor:", file)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
# import os
#
# async def change_audio_speed(input_file: str, output_file: str, speed: float):
#     # speed < 1 → sekinroq, speed > 1 → tezroq
#     cmd = [
#         "ffmpeg", "-y", "-i", input_file,
#         "-filter:a", f"atempo={speed}",
#         output_file
#     ]
#     process = await asyncio.create_subprocess_exec(*cmd)
#     await process.wait()
#     return output_file
#
# async def main():
#     input_mp3 = "input.mp3"
#
#     slowed = await change_audio_speed(input_mp3, "slowed.mp3", 0.85)
#     speeded = await change_audio_speed(input_mp3, "speeded.mp3", 1.25)
#
#     print("✅ Slowed:", slowed)
#     print("✅ Speeded:", speeded)
#
# if __name__ == "__main__":
#     asyncio.run(main())


async def make_slowed_deep(input_file: str, output_file: str):
    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-filter_complex", "[0:a]asetrate=44100*0.85,aresample=44100,atempo=1.0,volume=1.05[a]",
        "-map", "[a]", output_file
    ]
    process = await asyncio.create_subprocess_exec(*cmd)
    await process.wait()
    return output_file

async def main():
    slowed_file = await make_slowed_deep("input.mp3", "slowed_deep.mp3")
    print("✅ Slowed & Deep version:", slowed_file)

if __name__ == "__main__":
    asyncio.run(main())
