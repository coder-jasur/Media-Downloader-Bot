from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from src.app.keyboards.inline import auido_effect
from src.app.texts import user_texts, music_and_audio_process_texts

user_commands_router = Router()

@user_commands_router.message(Command("about"))
async def handled_command_about(message: Message, lang: str):
    await message.answer(user_texts["about"][lang])

@user_commands_router.message(Command("audio_effect"))
async def handled_command_about(message: Message, lang: str):
    await message.answer(music_and_audio_process_texts["audio_effect"][lang], reply_markup=auido_effect)