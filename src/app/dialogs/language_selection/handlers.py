import asyncpg
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from asyncpg import Connection

from src.app.database.queries.referals import ReferalDataBaseActions
from src.app.database.queries.users import UserDataBaseActions
from src.app.utils.i18n import get_translator


async def on_language_selection(
        _,
        button: Button,
        dialog_manager: DialogManager
):
    pool: asyncpg.Pool = dialog_manager.middleware_data.get("pool")
    user_actions = UserDataBaseActions(pool)
    user = dialog_manager.event.from_user
    selected_lang = button.widget_id  # "uz", "ru", "en" ...

    try:
        # 1️⃣ Referral kodni olish va qayta ishlash
        start_data = dialog_manager.start_data
        referral_code = None

        if start_data and isinstance(start_data, dict):
            referral_code = start_data.get("referral_code")

        if referral_code:
            print(f"✅ Processing referral: {referral_code}")
            referrals_actions = ReferalDataBaseActions(pool)
            try:
                await referrals_actions.increment_referal_members_count(
                    referral_id=referral_code
                )
            except Exception as ref_error:
                print(f"❌ Referral error: {ref_error}")
                # Referral xatosi asosiy jarayonni to'xtatmasin

        # 2️⃣ Foydalanuvchini tekshirish va qo'shish
        user_data = await user_actions.get_user(user.id)

        if not user_data:
            # Yangi foydalanuvchi
            await user_actions.add_user(
                tg_id=user.id,
                username=user.username or user.full_name,
                language=selected_lang
            )
            print(f"✅ New user added: {user.id} with lang: {selected_lang}")
        else:
            # Mavjud foydalanuvchi - tilni yangilash
            await user_actions.update_user_lang(selected_lang, user.id)
            print(f"✅ User {user.id} language updated to: {selected_lang}")

        # 3️⃣ Dialog'ni yopish
        await dialog_manager.done()

        # 4️⃣ Start xabarini yuborish
        _ = get_translator(selected_lang).gettext

        # ⚠️ edit_text o'rniga answer ishlatish (xavfsizroq)
        if isinstance(dialog_manager.event, CallbackQuery):
            # Dialog xabarini o'chirish
            try:
                await dialog_manager.event.message.delete()
            except Exception:
                pass  # Agar o'chirib bo'lmasa, davom etamiz

            # Yangi xabar yuborish
            await dialog_manager.event.message.answer(
                _("Start text").format(user.first_name)
            )

    except Exception as e:
        print(f"❌ Critical error in language selection: {e}")
        import traceback
        traceback.print_exc()  # To'liq error logini ko'rsatish

        # Foydalanuvchiga xabar berish
        try:
            await dialog_manager.event.message.answer(
                "❌ Xatolik yuz berdi. Iltimos, /start buyrug'ini qayta yuboring."
            )
        except Exception:
            pass

