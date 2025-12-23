from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from prisma import Prisma

from bot.formatters.messages import (
    format_buy_menu,
    format_coin_networks,
    format_buy_amount,
    format_buy_confirm,
    format_transaction_success,
    format_error,
    format_insufficient_balance,
    Emoji,
)
from bot.keyboards.inline import (
    CallbackData,
    get_coins_keyboard,
    get_networks_keyboard,
    get_confirm_keyboard,
    get_back_keyboard,
    get_cancel_keyboard,
)
from bot.utils.helpers import parse_amount, idr_to_crypto
from bot.services.oxapay import OxaPayService
from bot.db.queries import (
    get_coin_settings,
    create_crypto_order,
    update_balance,
)
from bot.config import config

router = Router()

USD_TO_IDR = Decimal("16000")


class BuyStates(StatesGroup):
    selecting_coin = State()
    selecting_network = State()
    entering_amount = State()
    entering_wallet = State()
    confirming = State()


@router.callback_query(F.data == CallbackData.MENU_BUY)
async def show_buy_menu(callback: CallbackQuery, state: FSMContext, db: Prisma, user: Optional[dict] = None, **kwargs):
    if not user or user.status != "ACTIVE":
        await callback.answer("Silakan daftar terlebih dahulu.", show_alert=True)
        return
    
    oxapay = OxaPayService(
        merchant_api_key=config.oxapay.merchant_api_key,
        payout_api_key=config.oxapay.payout_api_key,
        webhook_secret=config.oxapay.webhook_secret,
    )
    
    try:
        coins = await oxapay.get_supported_coins()
    finally:
        await oxapay.close()
    
    await state.set_state(BuyStates.selecting_coin)
    
    await callback.message.edit_text(
        format_buy_menu(),
        reply_markup=get_coins_keyboard(coins, "buy"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy:coin:"))
async def select_buy_coin(callback: CallbackQuery, state: FSMContext, **kwargs):
    coin = callback.data.split(":")[-1]
    
    oxapay = OxaPayService(
        merchant_api_key=config.oxapay.merchant_api_key,
        payout_api_key=config.oxapay.payout_api_key,
        webhook_secret=config.oxapay.webhook_secret,
    )
    
    try:
        networks = await oxapay.get_coin_networks(coin)
        rate_usd = await oxapay.get_exchange_rate(coin, "USD")
    finally:
        await oxapay.close()
    
    if not networks:
        await callback.answer("Network tidak tersedia.", show_alert=True)
        return
    
    rate_idr = rate_usd * USD_TO_IDR if rate_usd else None
    
    await state.update_data(coin=coin)
    await state.set_state(BuyStates.selecting_network)
    
    await callback.message.edit_text(
        format_coin_networks(coin),
        reply_markup=get_networks_keyboard(networks, coin, "buy", rate_idr),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy:network:"))
async def select_buy_network(callback: CallbackQuery, state: FSMContext, db: Prisma, **kwargs):
    parts = callback.data.split(":")
    coin = parts[2]
    network = parts[3]
    
    coin_setting = await get_coin_settings(db, coin, network)
    
    if not coin_setting:
        margin = Decimal("2")
    else:
        margin = coin_setting.buyMargin
    
    oxapay = OxaPayService(
        merchant_api_key=config.oxapay.merchant_api_key,
        payout_api_key=config.oxapay.payout_api_key,
        webhook_secret=config.oxapay.webhook_secret,
    )
    
    try:
        rate_usd = await oxapay.get_exchange_rate(coin, "USD")
        networks = await oxapay.get_coin_networks(coin)
    finally:
        await oxapay.close()
    
    if not rate_usd:
        await callback.answer("Gagal mendapatkan rate.", show_alert=True)
        return
    
    rate_idr = rate_usd * USD_TO_IDR
    
    network_info = next((n for n in networks if n["network"] == network), None)
    network_fee = network_info["withdraw_fee"] if network_info else Decimal("0")
    
    await state.update_data(
        coin=coin,
        network=network,
        rate_idr=float(rate_idr),
        margin=float(margin),
        network_fee=float(network_fee),
    )
    await state.set_state(BuyStates.entering_amount)
    
    await callback.message.edit_text(
        format_buy_amount(coin, network, rate_idr, margin),
        reply_markup=get_cancel_keyboard("buy:back"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(BuyStates.entering_amount)
async def process_buy_amount(message: Message, state: FSMContext, db: Prisma, user: Optional[dict] = None, **kwargs):
    amount_idr = parse_amount(message.text)
    
    if not amount_idr or amount_idr < Decimal("10000"):
        await message.answer(
            format_error("Jumlah minimal pembelian adalah Rp 10.000"),
            reply_markup=get_cancel_keyboard("buy:back"),
            parse_mode="HTML"
        )
        return
    
    if not user:
        await message.answer(format_error("User tidak ditemukan."), parse_mode="HTML")
        return
    
    balance = user.balance.amount if user.balance else Decimal("0")
    
    data = await state.get_data()
    rate_idr = Decimal(str(data["rate_idr"]))
    margin = Decimal(str(data["margin"]))
    network_fee = Decimal(str(data["network_fee"]))
    
    calc = idr_to_crypto(amount_idr, rate_idr, margin, network_fee)
    
    if calc.get("error"):
        await message.answer(
            format_error(calc["error"]),
            reply_markup=get_cancel_keyboard("buy:back"),
            parse_mode="HTML"
        )
        return
    
    total_idr = calc["total_idr"]
    
    if total_idr > balance:
        await message.answer(
            format_insufficient_balance(total_idr, balance),
            reply_markup=get_cancel_keyboard("buy:back"),
            parse_mode="HTML"
        )
        return
    
    await state.update_data(
        amount_idr=float(amount_idr),
        crypto_amount=float(calc["crypto_amount"]),
        total_idr=float(total_idr),
        network_fee_idr=float(calc["network_fee_idr"]),
    )
    await state.set_state(BuyStates.entering_wallet)
    
    await message.answer(
        f"<b>Alamat Wallet</b>\n\n"
        f"Masukkan alamat wallet {data['coin']} ({data['network']}):",
        reply_markup=get_cancel_keyboard("buy:back"),
        parse_mode="HTML"
    )


@router.message(BuyStates.entering_wallet)
async def process_wallet_address(message: Message, state: FSMContext, **kwargs):
    wallet = message.text.strip()
    
    if len(wallet) < 20:
        await message.answer(
            format_error("Alamat wallet tidak valid."),
            reply_markup=get_cancel_keyboard("buy:back"),
            parse_mode="HTML"
        )
        return
    
    data = await state.get_data()
    await state.update_data(wallet_address=wallet)
    await state.set_state(BuyStates.confirming)
    
    await message.answer(
        format_buy_confirm(
            coin=data["coin"],
            network=data["network"],
            fiat_amount=Decimal(str(data["amount_idr"])),
            crypto_amount=Decimal(str(data["crypto_amount"])),
            rate=Decimal(str(data["rate_idr"])) * (Decimal("1") + Decimal(str(data["margin"])) / Decimal("100")),
            network_fee=Decimal(str(data["network_fee"])),
            total=Decimal(str(data["total_idr"])),
        ),
        reply_markup=get_confirm_keyboard("buy", "process"),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "buy:confirm:process")
async def confirm_buy(callback: CallbackQuery, state: FSMContext, db: Prisma, user: Optional[dict] = None, **kwargs):
    data = await state.get_data()
    
    if not user:
        await callback.answer("User tidak ditemukan.", show_alert=True)
        return
    
    balance = user.balance.amount if user.balance else Decimal("0")
    total_idr = Decimal(str(data["total_idr"]))
    
    if total_idr > balance:
        await callback.message.edit_text(
            format_insufficient_balance(total_idr, balance),
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    order = await create_crypto_order(
        db=db,
        user_id=user.id,
        order_type="BUY",
        coin_symbol=data["coin"],
        network=data["network"],
        crypto_amount=Decimal(str(data["crypto_amount"])),
        fiat_amount=Decimal(str(data["amount_idr"])),
        rate=Decimal(str(data["rate_idr"])),
        margin=Decimal(str(data["margin"])),
        network_fee=Decimal(str(data["network_fee"])),
        wallet_address=data["wallet_address"],
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    
    await update_balance(db, user.id, -total_idr)
    
    await db.cryptoorder.update(
        where={"id": order.id},
        data={"status": "PROCESSING"}
    )
    
    oxapay = OxaPayService(
        merchant_api_key=config.oxapay.merchant_api_key,
        payout_api_key=config.oxapay.payout_api_key,
        webhook_secret=config.oxapay.webhook_secret,
    )
    
    try:
        result = await oxapay.create_payout(
            address=data["wallet_address"],
            amount=Decimal(str(data["crypto_amount"])),
            currency=data["coin"],
            network=data["network"],
            description=f"Order {order.id}",
        )
        
        if result.success:
            await db.cryptoorder.update(
                where={"id": order.id},
                data={
                    "status": "COMPLETED",
                    "oxapayPayoutId": result.payout_id,
                    "txHash": result.tx_hash,
                }
            )
            
            await db.transaction.create(
                data={
                    "userId": user.id,
                    "type": "BUY",
                    "amount": total_idr,
                    "status": "COMPLETED",
                    "description": f"Beli {data['crypto_amount']:.8f} {data['coin']}",
                    "metadata": {"orderId": order.id},
                }
            )
            
            await state.clear()
            
            await callback.message.edit_text(
                format_transaction_success("Beli Crypto", total_idr) + 
                f"\n\nAnda menerima: <b>{data['crypto_amount']:.8f} {data['coin']}</b>\n"
                f"Ke: <code>{data['wallet_address'][:20]}...</code>",
                reply_markup=get_back_keyboard(),
                parse_mode="HTML"
            )
        else:
            await update_balance(db, user.id, total_idr)
            await db.cryptoorder.update(
                where={"id": order.id},
                data={"status": "FAILED"}
            )
            
            await callback.message.edit_text(
                format_error(f"Payout gagal: {result.error}"),
                reply_markup=get_back_keyboard(),
                parse_mode="HTML"
            )
    except Exception as e:
        await update_balance(db, user.id, total_idr)
        await db.cryptoorder.update(
            where={"id": order.id},
            data={"status": "FAILED"}
        )
        
        await callback.message.edit_text(
            format_error(f"Terjadi kesalahan: {str(e)}"),
            reply_markup=get_back_keyboard(),
            parse_mode="HTML"
        )
    finally:
        await oxapay.close()
    
    await callback.answer()


@router.callback_query(F.data == "buy:cancel:process")
async def cancel_buy(callback: CallbackQuery, state: FSMContext, **kwargs):
    await state.clear()
    
    await callback.message.edit_text(
        "Pembelian dibatalkan.",
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "buy:back")
async def back_to_buy_coins(callback: CallbackQuery, state: FSMContext, **kwargs):
    oxapay = OxaPayService(
        merchant_api_key=config.oxapay.merchant_api_key,
        payout_api_key=config.oxapay.payout_api_key,
        webhook_secret=config.oxapay.webhook_secret,
    )
    
    try:
        coins = await oxapay.get_supported_coins()
    finally:
        await oxapay.close()
    
    await state.set_state(BuyStates.selecting_coin)
    
    await callback.message.edit_text(
        format_buy_menu(),
        reply_markup=get_coins_keyboard(coins, "buy"),
        parse_mode="HTML"
    )
    await callback.answer()
