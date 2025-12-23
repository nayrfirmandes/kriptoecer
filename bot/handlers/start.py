from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from prisma import Prisma
from typing import Optional

from bot.formatters.messages import format_welcome, format_terms, format_main_menu
from bot.keyboards.inline import get_terms_keyboard, get_main_menu_keyboard, CallbackData
from bot.db.queries import get_user_by_telegram_id

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: Prisma, user: Optional[dict] = None, **kwargs):
    await state.clear()
    
    if user:
        if user.status == "INACTIVE":
            await message.answer(
                "⚠️ <b>Akun Tidak Aktif</b>\n\n"
                "Akun Anda tidak aktif karena tidak ada aktivitas selama 6 bulan.\n"
                "Silakan daftar ulang untuk mengaktifkan kembali.",
                parse_mode="HTML"
            )
            await message.answer(
                format_welcome(),
                reply_markup=get_terms_keyboard(),
                parse_mode="HTML"
            )
            return
        
        if user.status == "BANNED":
            await message.answer(
                "🚫 <b>Akun Diblokir</b>\n\n"
                "Akun Anda telah diblokir. Hubungi support untuk informasi lebih lanjut.",
                parse_mode="HTML"
            )
            return
        
        if user.status == "PENDING":
            await message.answer(
                format_terms(),
                reply_markup=get_terms_keyboard(),
                parse_mode="HTML"
            )
            return
        
        balance = user.balance.amount if user.balance else 0
        name = user.firstName or user.username or "User"
        
        await message.answer(
            format_main_menu(balance, name),
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            format_welcome(),
            reply_markup=get_terms_keyboard(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == CallbackData.BACK_MENU)
async def back_to_menu(callback: CallbackQuery, state: FSMContext, db: Prisma, user: Optional[dict] = None, **kwargs):
    await state.clear()
    
    if not user or user.status != "ACTIVE":
        await callback.message.edit_text(
            format_welcome(),
            reply_markup=get_terms_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    balance = user.balance.amount if user.balance else 0
    name = user.firstName or user.username or "User"
    
    await callback.message.edit_text(
        format_main_menu(balance, name),
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
