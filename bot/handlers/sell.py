from decimal import Decimal
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from prisma import Prisma

from bot.formatters.messages import (
    format_sell_menu,
    format_coin_networks,
    format_sell_confirm,
    format_error,
    Emoji,
)
from bot.keyboards.inline import (
    CallbackData,
    get_coins_keyboard,
    get_networks_keyboard,
    get_back_keyboard,
    get_cancel_keyboard,
)
from bot.utils.helpers import parse_crypto_amount, calculate_sell_price
from bot.services.oxapay import OxaPayService
from bot.db.queries import (
    get_user_by_telegram_id,
    get_coin_settings,
    create_crypto_order,
)
from bot.config import config

router = Router()

USD_TO_IDR = Decimal("16000")


class SellStates(StatesGroup):
    selecting_coin = State()
    selecting_network = State()
    entering_amount = State()
    awaiting_deposit = State()


@router.callback_query(F.data == CallbackData.MENU_SELL)
async def show_sell_menu(callback: CallbackQuery, state: FSMContext, db: Prisma, **kwargs):
    user = await get_user_by_telegram_id(db, callback.from_user.id)
    
    if not user or user.status != "ACTIVE":
        await callback.answer("Silakan daftar terlebih dahulu.", show_alert=True)
        return
    
    oxapay = OxaPayService(
        api_key=config.oxapay.api_key,
        merchant_id=config.oxapay.merchant_id,
        webhook_secret=config.oxapay.webhook_secret,
    )
    
    try:
        coins = await oxapay.get_supported_coins()
    finally:
        await oxapay.close()
    
    await state.set_state(SellStates.selecting_coin)
    
    await callback.message.edit_text(
        format_sell_menu(),
        reply_markup=get_coins_keyboard(coins, "sell"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sell:coin:"))
async def select_sell_coin(callback: CallbackQuery, state: FSMContext, **kwargs):
    coin = callback.data.split(":")[-1]
    
    oxapay = OxaPayService(
        api_key=config.oxapay.api_key,
        merchant_id=config.oxapay.merchant_id,
        webhook_secret=config.oxapay.webhook_secret,
    )
    
    try:
        networks = await oxapay.get_coin_networks(coin)
    finally:
        await oxapay.close()
    
    if not networks:
        await callback.answer("Network tidak tersedia.", show_alert=True)
        return
    
    await state.update_data(coin=coin)
    await state.set_state(SellStates.selecting_network)
    
    await callback.message.edit_text(
        format_coin_networks(coin),
        reply_markup=get_networks_keyboard(networks, coin, "sell"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sell:network:"))
async def select_sell_network(callback: CallbackQuery, state: FSMContext, db: Prisma, **kwargs):
    parts = callback.data.split(":")
    coin = parts[2]
    network = parts[3]
    
    coin_setting = await get_coin_settings(db, coin, network)
    
    if not coin_setting:
        margin = Decimal("2")
    else:
        margin = coin_setting.sellMargin
    
    oxapay = OxaPayService(
        api_key=config.oxapay.api_key,
        merchant_id=config.oxapay.merchant_id,
        webhook_secret=config.oxapay.webhook_secret,
    )
    
    try:
        rate_usd = await oxapay.get_exchange_rate(coin, "USD")
    finally:
        await oxapay.close()
    
    if not rate_usd:
        await callback.answer("Gagal mendapatkan rate.", show_alert=True)
        return
    
    rate_idr = rate_usd * USD_TO_IDR
    rate_with_margin = rate_idr * (Decimal("1") - margin / Decimal("100"))
    
    await state.update_data(
        coin=coin,
        network=network,
        rate_idr=float(rate_idr),
        margin=float(margin),
    )
    await state.set_state(SellStates.entering_amount)
    
    await callback.message.edit_text(
        f"{Emoji.SELL} <b>Jual {coin} ({network})</b>\n\n"
        f"{Emoji.CHART} Rate: <b>Rp {rate_with_margin:,.0f}</b> / {coin}\n"
        f"{Emoji.INFO} Termasuk margin {margin}%\n\n"
        f"Masukkan jumlah <b>{coin}</b> yang ingin dijual:\n"
        f"<i>Contoh: 0.001</i>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(SellStates.entering_amount)
async def process_sell_amount(message: Message, state: FSMContext, db: Prisma, **kwargs):
    crypto_amount = parse_crypto_amount(message.text)
    
    if not crypto_amount or crypto_amount <= 0:
        await message.answer(
            format_error("Jumlah tidak valid."),
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    
    data = await state.get_data()
    rate_idr = Decimal(str(data["rate_idr"]))
    margin = Decimal(str(data["margin"]))
    
    calc = calculate_sell_price(crypto_amount, rate_idr, margin)
    fiat_amount = calc["total"]
    
    if fiat_amount < Decimal("10000"):
        await message.answer(
            format_error("Jumlah terlalu kecil. Minimum penjualan senilai Rp 10.000"),
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        return
    
    user = await get_user_by_telegram_id(db, message.from_user.id)
    
    oxapay = OxaPayService(
        api_key=config.oxapay.api_key,
        merchant_id=config.oxapay.merchant_id,
        webhook_secret=config.oxapay.webhook_secret,
    )
    
    try:
        webhook_url = f"https://{config.oxapay.webhook_secret}/webhook/oxapay"
        
        result = await oxapay.create_payment(
            amount=crypto_amount,
            currency=data["coin"],
            network=data["network"],
            order_id=f"SELL_{user.id}_{datetime.utcnow().timestamp()}",
            callback_url=webhook_url,
            lifetime=3600,
        )
        
        if not result.success:
            await message.answer(
                format_error(f"Gagal membuat address: {result.error}"),
                reply_markup=get_cancel_keyboard(),
                parse_mode="HTML"
            )
            return
        
        order = await create_crypto_order(
            db=db,
            user_id=user.id,
            order_type="SELL",
            coin_symbol=data["coin"],
            network=data["network"],
            crypto_amount=crypto_amount,
            fiat_amount=fiat_amount,
            rate=rate_idr,
            margin=margin,
            network_fee=Decimal("0"),
            deposit_address=result.address,
            oxapayPaymentId=result.payment_id,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        
        await db.cryptoorder.update(
            where={"id": order.id},
            data={"status": "AWAITING_CRYPTO"}
        )
        
        await state.clear()
        
        await message.answer(
            format_sell_confirm(
                coin=data["coin"],
                network=data["network"],
                crypto_amount=crypto_amount,
                fiat_amount=fiat_amount,
                rate=calc["rate_with_margin"],
                deposit_address=result.address,
            ),
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.answer(
            format_error(f"Terjadi kesalahan: {str(e)}"),
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
    finally:
        await oxapay.close()


@router.callback_query(F.data == "sell:back")
async def back_to_sell_coins(callback: CallbackQuery, state: FSMContext, **kwargs):
    oxapay = OxaPayService(
        api_key=config.oxapay.api_key,
        merchant_id=config.oxapay.merchant_id,
        webhook_secret=config.oxapay.webhook_secret,
    )
    
    try:
        coins = await oxapay.get_supported_coins()
    finally:
        await oxapay.close()
    
    await state.set_state(SellStates.selecting_coin)
    
    await callback.message.edit_text(
        format_sell_menu(),
        reply_markup=get_coins_keyboard(coins, "sell"),
        parse_mode="HTML"
    )
    await callback.answer()
