from decimal import Decimal
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import Optional


class CallbackData:
    AGREE_TERMS = "signup:agree"
    SKIP_REFERRAL = "signup:skip_referral"
    
    MENU_BALANCE = "menu:balance"
    MENU_BUY = "menu:buy"
    MENU_SELL = "menu:sell"
    MENU_TOPUP = "menu:topup"
    MENU_WITHDRAW = "menu:withdraw"
    MENU_HISTORY = "menu:history"
    MENU_REFERRAL = "menu:referral"
    MENU_RATES = "menu:rates"
    MENU_HELP = "menu:help"
    
    BACK_MENU = "back:menu"
    BACK = "back"
    CANCEL = "cancel"


def get_terms_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Setuju & Daftar",
            callback_data=CallbackData.AGREE_TERMS
        )
    )
    return builder.as_markup()


def get_skip_referral_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Lewati",
            callback_data=CallbackData.SKIP_REFERRAL
        )
    )
    return builder.as_markup()


def get_location_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="Bagikan Lokasi", request_location=True)
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="Bagikan Nomor HP", request_contact=True)
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Beli Crypto", callback_data=CallbackData.MENU_BUY),
        InlineKeyboardButton(text="Jual Crypto", callback_data=CallbackData.MENU_SELL),
    )
    builder.row(
        InlineKeyboardButton(text="Cek Harga", callback_data=CallbackData.MENU_RATES),
        InlineKeyboardButton(text="Saldo", callback_data=CallbackData.MENU_BALANCE),
    )
    builder.row(
        InlineKeyboardButton(text="Deposit", callback_data=CallbackData.MENU_TOPUP),
        InlineKeyboardButton(text="Withdraw", callback_data=CallbackData.MENU_WITHDRAW),
    )
    builder.row(
        InlineKeyboardButton(text="Riwayat", callback_data=CallbackData.MENU_HISTORY),
        InlineKeyboardButton(text="Referral", callback_data=CallbackData.MENU_REFERRAL),
    )
    builder.row(
        InlineKeyboardButton(text="Bantuan", callback_data=CallbackData.MENU_HELP),
    )
    return builder.as_markup()


def get_balance_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Deposit", callback_data=CallbackData.MENU_TOPUP),
        InlineKeyboardButton(text="Withdraw", callback_data=CallbackData.MENU_WITHDRAW),
    )
    builder.row(
        InlineKeyboardButton(text="Kembali", callback_data=CallbackData.BACK_MENU),
    )
    return builder.as_markup()


def get_coins_keyboard(coins: list[dict], action: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for i in range(0, len(coins), 2):
        row = []
        for j in range(2):
            if i + j < len(coins):
                symbol = coins[i + j]["symbol"]
                row.append(
                    InlineKeyboardButton(
                        text=symbol,
                        callback_data=f"{action}:coin:{symbol}"
                    )
                )
        builder.row(*row)
    
    builder.row(
        InlineKeyboardButton(text="Kembali", callback_data=CallbackData.BACK_MENU),
    )
    return builder.as_markup()


def get_networks_keyboard(networks: list[dict], coin: str, action: str, rate_idr: Optional[Decimal] = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for net in networks:
        network = net["network"]
        fee = net.get("withdraw_fee", Decimal("0"))
        
        if rate_idr and fee:
            fee_idr = Decimal(str(fee)) * rate_idr
            fee_text = f"Fee: Rp {fee_idr:,.0f}"
        else:
            fee_text = f"Fee: {fee} {coin}"
        
        builder.row(
            InlineKeyboardButton(
                text=f"{network} ({fee_text})",
                callback_data=f"{action}:network:{coin}:{network}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="Kembali", callback_data=f"{action}:back"),
    )
    return builder.as_markup()


def get_confirm_keyboard(action: str, order_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Konfirmasi",
            callback_data=f"{action}:confirm:{order_id}"
        ),
        InlineKeyboardButton(
            text="Batal",
            callback_data=f"{action}:cancel:{order_id}"
        ),
    )
    return builder.as_markup()


def get_topup_methods_keyboard(methods: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for method in methods:
        builder.row(
            InlineKeyboardButton(
                text=method['name'],
                callback_data=f"topup:method:{method['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="Kembali", callback_data=CallbackData.BACK_MENU),
    )
    return builder.as_markup()


def get_topup_confirm_keyboard(deposit_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Sudah Transfer",
            callback_data=f"topup:confirm:{deposit_id}"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="Batal",
            callback_data=f"topup:cancel:{deposit_id}"
        ),
    )
    return builder.as_markup()


def get_withdraw_methods_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Bank Transfer", callback_data="withdraw:method:bank"),
        InlineKeyboardButton(text="E-Wallet", callback_data="withdraw:method:ewallet"),
    )
    builder.row(
        InlineKeyboardButton(text="Kembali", callback_data=CallbackData.BACK_MENU),
    )
    return builder.as_markup()


def get_ewallet_options_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    ewallets = ["GoPay", "OVO", "DANA", "ShopeePay", "LinkAja"]
    
    for i in range(0, len(ewallets), 2):
        row = []
        for j in range(2):
            if i + j < len(ewallets):
                ew = ewallets[i + j]
                row.append(
                    InlineKeyboardButton(
                        text=ew,
                        callback_data=f"withdraw:ewallet:{ew}"
                    )
                )
        builder.row(*row)
    
    builder.row(
        InlineKeyboardButton(text="Kembali", callback_data="withdraw:back"),
    )
    return builder.as_markup()


def get_back_keyboard(callback_data: str = CallbackData.BACK_MENU) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Kembali", callback_data=callback_data),
    )
    return builder.as_markup()


def get_cancel_keyboard(back_callback: str = CallbackData.BACK_MENU) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Batal", callback_data=back_callback),
    )
    return builder.as_markup()


def get_history_pagination_keyboard(
    page: int,
    total_pages: int,
    tx_type: Optional[str] = None
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    filter_prefix = f":{tx_type}" if tx_type else ""
    
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Prev",
                callback_data=f"history:page{filter_prefix}:{page - 1}"
            )
        )
    
    nav_buttons.append(
        InlineKeyboardButton(
            text=f"{page}/{total_pages}",
            callback_data="history:current"
        )
    )
    
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Next",
                callback_data=f"history:page{filter_prefix}:{page + 1}"
            )
        )
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    builder.row(
        InlineKeyboardButton(text="Kembali", callback_data=CallbackData.BACK_MENU),
    )
    return builder.as_markup()
