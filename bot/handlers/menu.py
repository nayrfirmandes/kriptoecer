from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from prisma import Prisma

from bot.formatters.messages import format_referral_info, Emoji
from bot.keyboards.inline import CallbackData, get_back_keyboard
from bot.db.queries import get_user_by_telegram_id, get_referral_count, get_referral_bonus_earned

router = Router()


@router.callback_query(F.data == CallbackData.MENU_REFERRAL)
async def show_referral(callback: CallbackQuery, db: Prisma, **kwargs):
    user = await get_user_by_telegram_id(db, callback.from_user.id)
    
    if not user:
        await callback.answer("Silakan daftar terlebih dahulu.", show_alert=True)
        return
    
    referral_count = await get_referral_count(db, user.id)
    bonus_earned = await get_referral_bonus_earned(db, user.id)
    
    await callback.message.edit_text(
        format_referral_info(user.referralCode, referral_count, bonus_earned),
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == CallbackData.MENU_HELP)
async def show_help(callback: CallbackQuery, **kwargs):
    help_text = f"""
{Emoji.HELP} <b>Bantuan</b>

{Emoji.INFO} <b>Cara Menggunakan Bot:</b>

1️⃣ <b>Top Up Saldo</b>
   Transfer ke rekening/e-wallet kami, konfirmasi, tunggu approval.

2️⃣ <b>Beli Crypto</b>
   Pilih coin → Masukkan jumlah → Konfirmasi → Crypto terkirim ke wallet Anda.

3️⃣ <b>Jual Crypto</b>
   Pilih coin → Kirim ke address kami → Saldo bertambah.

4️⃣ <b>Withdraw Saldo</b>
   Request withdraw → Tunggu proses → Dana terkirim.

{Emoji.PHONE} <b>Hubungi Support:</b>
WhatsApp: +62xxx (hubungi admin)

{Emoji.WARNING} <b>Penting:</b>
- Pastikan alamat wallet benar sebelum transaksi
- Transaksi crypto bersifat final
- Simpan bukti transaksi Anda
"""
    
    await callback.message.edit_text(
        help_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
