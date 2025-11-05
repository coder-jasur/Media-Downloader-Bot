import asyncpg
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.app.common.referals_id_genrator import generate_ref_id
from src.app.database.queries.referals import ReferalDataBaseActions
from src.app.handlers.admin.menu.helpers import _show_referrals_menu_message
from src.app.handlers.admin.menu.menu import _handle_referrals_menu
from src.app.keyboards.callback_data import ReferralCD
from src.app.keyboards.inline import (
    delite_referral_menu,
    menu_referrals_kb,
    referals_menu_kbd,
    back_to_admin_menu_keyboards
)
from src.app.states.admin.add_referal import AddReferalSG
from src.app.utils.enums.actions import ReferalsActions
from src.app.utils.i18n import get_translator

referrals_router = Router(name="referrals_admin")


@referrals_router.callback_query(ReferralCD.filter())
async def handle_referral_actions(
        call: CallbackQuery,
        callback_data: ReferralCD,
        pool: asyncpg.Pool,
        lang: str,
        state: FSMContext
):
    """Referral action handler"""
    referrals_actions = ReferalDataBaseActions(pool)
    _ = get_translator(lang).gettext

    if callback_data.action == ReferalsActions.DELETE_REFERAL:
        await call.message.edit_text(
            _("Delete referal choose"),
            reply_markup=delite_referral_menu(callback_data.referral_id, lang)
        )
        return

    elif callback_data.action == ReferalsActions.SURE_DELETE:
        await referrals_actions.delite_referal(callback_data.referral_id)
        await call.answer(_("Delete referal passed"))

        # Menyu ko'rsatish
        referrals_data = await referrals_actions.get_all_referals()
        text = (
            _("Referals menu title")
            if referrals_data
            else _("Empty referals menu title")
        )
        await call.message.edit_text(
            text,
            reply_markup=referals_menu_kbd(referrals_data, lang)
        )
        return

    elif callback_data.action == ReferalsActions.ADD_REFERALS:
        await state.set_state(AddReferalSG.get_referal_name)
        await call.message.edit_text(
            _("Get referal name"),
            reply_markup=back_to_admin_menu_keyboards(lang)
        )
        return

    elif callback_data.action == ReferalsActions.NOT_SURE_DELETE:
        pass  # Do nothing

    # Referral menyusini ko'rsatish
    referral = await referrals_actions.get_referal(callback_data.referral_id)
    await call.message.edit_text(
        _("Referal formant info").format(referral[1], referral[2], referral[0]),
        reply_markup=menu_referrals_kb(callback_data.referral_id, lang)
    )


@referrals_router.message(AddReferalSG.get_referal_name)
async def add_referral(message: Message, state: FSMContext, pool: asyncpg.Pool, lang: str):
    """Referral qo'shish"""
    _ = get_translator(lang).gettext

    if not message.text:
        await message.answer(_("Send only text"))
        return

    referral_actions = ReferalDataBaseActions(pool)
    referral_id = generate_ref_id()
    await referral_actions.add_referal(referral_id, message.text)

    await state.clear()
    await message.answer(_("Referral added successfully!"))

    # Menyu ko'rsatish
    await _show_referrals_menu_message(message, pool, lang)


@referrals_router.callback_query(F.data == "back_to_menu_referrals")
async def back_to_referrals_menu(call: CallbackQuery, pool: asyncpg.Pool, lang: str):
    """Referrals menyuga qaytish"""
    await _handle_referrals_menu(call, pool, lang)