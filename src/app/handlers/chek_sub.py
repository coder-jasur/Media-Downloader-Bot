import asyncpg
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from src.app.database.queries.channels import ChannelDataBaseActions
from src.app.database.queries.users import UserDataBaseActions
from src.app.keyboards.inline import not_channels_button
from src.app.states.check_channel_sub import ChooseLanguageSG
from src.app.utils.i18n import get_translator

check_sub_router = Router()


@check_sub_router.callback_query(F.data == "check_sub")
async def check_channel_sub(
        call: CallbackQuery,
        dialog_manager: DialogManager,
        pool: asyncpg.Pool,
        bot: Bot,
        lang: str,
):
    _ = get_translator(lang).gettext
    channel_actions = ChannelDataBaseActions(pool)
    user_actions = UserDataBaseActions(pool)

    # call.from_user.id dan foydalanish (dialog_manager.event emas)
    user_data = await user_actions.get_user(call.from_user.id)
    channel_data = await channel_actions.get_all_channels()
    not_sub_channels = []

    # Majburiy kanallarga obuna tekshirish
    for channel in channel_data:
        # channel[3] tekshirish - string yoki boolean
        if channel[3] is True or channel[3] == "True" or channel[3] == True:
            try:
                user_status = await bot.get_chat_member(channel[0], call.from_user.id)
                if user_status.status not in ["member", "administrator", "creator"]:
                    not_sub_channels.append(channel)
            except Exception as e:
                # Kanal topilmasa yoki boshqa xato
                print(f"Error checking channel {channel[0]}: {e}")
                continue

    # Translation matnlari (yoki translation fayllaridan olish mumkin)
    if lang == "uz":
        subscription_text = "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling 👇"
    elif lang == "ru":
        subscription_text = "Чтобы пользоваться ботом, подпишитесь на эти каналы 👇"
    elif lang == "en":
        subscription_text = "To use the bot, please subscribe to these channels 👇"
    else:
        subscription_text = "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling 👇"

    if not not_sub_channels:

        if not user_data or not user_data[3]:
            await dialog_manager.start(ChooseLanguageSG.choose_language)
        else:
            await call.message.answer(_("Start text"))
            try:
                await call.message.delete()
            except:
                pass

    else:
        try:
            await call.message.edit_text(
                subscription_text,
                reply_markup=not_channels_button(not_sub_channels),
            )
        except Exception as e:
            print(f"Could not edit message: {e}")
            try:
                await call.message.answer(
                    subscription_text,
                    reply_markup=not_channels_button(not_sub_channels),
                )
                try:
                    await call.message.delete()
                except:
                    pass
            except Exception as e:
                print(f"Error sending subscription message: {e}")

    try:
        await call.answer()
    except:
        pass