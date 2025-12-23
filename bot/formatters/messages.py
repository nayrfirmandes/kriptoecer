from decimal import Decimal
from typing import Optional


class Emoji:
    WELCOME = "👋"
    MONEY = "💰"
    BALANCE = "💵"
    BUY = "🛒"
    SELL = "💸"
    TOPUP = "➕"
    WITHDRAW = "➖"
    HISTORY = "📜"
    SETTINGS = "⚙️"
    HELP = "❓"
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    PENDING = "⏳"
    PROCESSING = "🔄"
    CRYPTO = "🪙"
    WALLET = "👛"
    REFERRAL = "🎁"
    USER = "👤"
    PHONE = "📱"
    EMAIL = "📧"
    LOCATION = "📍"
    BACK = "◀️"
    NEXT = "▶️"
    HOME = "🏠"
    INFO = "ℹ️"
    LOCK = "🔒"
    UNLOCK = "🔓"
    STAR = "⭐"
    FIRE = "🔥"
    ROCKET = "🚀"
    CHART = "📊"
    BANK = "🏦"
    CHECK = "☑️"
    CLOCK = "🕐"


def format_currency(amount: Decimal, symbol: str = "IDR") -> str:
    if symbol == "IDR":
        return f"Rp {amount:,.0f}"
    return f"{amount:,.8f}".rstrip('0').rstrip('.') + f" {symbol}"


def format_welcome() -> str:
    return f"""
{Emoji.WELCOME} <b>Selamat Datang di CryptoBot!</b>

{Emoji.CRYPTO} Platform jual beli crypto terpercaya dengan:
{Emoji.SUCCESS} Transaksi cepat & aman
{Emoji.SUCCESS} Harga kompetitif
{Emoji.SUCCESS} Support 24/7

{Emoji.INFO} Silakan daftar untuk mulai trading!
"""


def format_terms() -> str:
    return f"""
{Emoji.LOCK} <b>Syarat & Ketentuan</b>

Dengan menggunakan layanan ini, Anda menyetujui:

1️⃣ Anda berusia minimal 18 tahun
2️⃣ Data yang diberikan adalah valid
3️⃣ Anda bertanggung jawab atas keamanan akun
4️⃣ Transaksi bersifat final setelah dikonfirmasi
5️⃣ Kami berhak membekukan akun yang mencurigakan

{Emoji.WARNING} Pastikan Anda memahami risiko trading crypto.
"""


def format_main_menu(balance: Decimal, name: str) -> str:
    return f"""
{Emoji.HOME} <b>Menu Utama</b>

{Emoji.USER} Halo, <b>{name}</b>!
{Emoji.BALANCE} Saldo: <b>{format_currency(balance)}</b>

{Emoji.INFO} Pilih menu di bawah:
"""


def format_rates(rates: dict, usd_to_idr: Decimal) -> str:
    coin_emojis = {
        "BTC": "🟠",
        "ETH": "🔷",
        "BNB": "🟡",
        "SOL": "🟣",
        "USDT": "🟢",
        "USDC": "🔵",
    }
    
    supported = ["BTC", "ETH", "BNB", "SOL", "USDT", "USDC"]
    
    lines = [f"{Emoji.CHART} <b>Harga Crypto Realtime</b>\n"]
    
    for symbol in supported:
        if symbol in rates:
            price_usd = Decimal(str(rates[symbol]))
            price_idr = price_usd * usd_to_idr
            emoji = coin_emojis.get(symbol, "🪙")
            lines.append(f"{emoji} <b>{symbol}</b>: {format_currency(price_idr)}")
    
    lines.append(f"\n{Emoji.CLOCK} <i>Update: Realtime dari OxaPay</i>")
    lines.append(f"{Emoji.INFO} Rate: $1 = Rp {usd_to_idr:,.0f}")
    
    return "\n".join(lines)


def format_balance(balance: Decimal) -> str:
    return f"""
{Emoji.WALLET} <b>Saldo Anda</b>

{Emoji.MONEY} <b>{format_currency(balance)}</b>

{Emoji.TOPUP} Top Up untuk menambah saldo
{Emoji.WITHDRAW} Withdraw untuk menarik saldo
"""


def format_signup_email() -> str:
    return f"""
{Emoji.EMAIL} <b>Masukkan Email</b>

Silakan kirim alamat email Anda yang aktif.
Email akan digunakan untuk notifikasi penting.

<i>Contoh: nama@email.com</i>
"""


def format_signup_whatsapp() -> str:
    return f"""
{Emoji.PHONE} <b>Masukkan Nomor WhatsApp</b>

Silakan kirim nomor WhatsApp Anda.
Format: 08xxx atau 628xxx

<i>Contoh: 081234567890</i>
"""


def format_signup_location() -> str:
    return f"""
{Emoji.LOCATION} <b>Bagikan Lokasi</b>

Silakan bagikan lokasi Anda untuk verifikasi.
Klik tombol di bawah untuk share lokasi.
"""


def format_signup_referral() -> str:
    return f"""
{Emoji.REFERRAL} <b>Kode Referral (Opsional)</b>

Jika Anda punya kode referral dari teman, masukkan sekarang.
Anda dan teman Anda akan mendapat bonus!

Atau klik "Lewati" untuk lanjut tanpa referral.
"""


def format_signup_success(referral_code: str) -> str:
    return f"""
{Emoji.SUCCESS} <b>Pendaftaran Berhasil!</b>

Selamat! Akun Anda sudah aktif.

{Emoji.REFERRAL} Kode referral Anda: <code>{referral_code}</code>
Bagikan ke teman untuk dapat bonus!

{Emoji.ROCKET} Selamat trading!
"""


def format_buy_menu() -> str:
    return f"""
{Emoji.BUY} <b>Beli Crypto</b>

Pilih cryptocurrency yang ingin Anda beli:
"""


def format_sell_menu() -> str:
    return f"""
{Emoji.SELL} <b>Jual Crypto</b>

Pilih cryptocurrency yang ingin Anda jual:
"""


def format_coin_networks(coin: str) -> str:
    return f"""
{Emoji.CRYPTO} <b>Pilih Network untuk {coin}</b>

Pilih network yang Anda inginkan:
"""


def format_buy_amount(coin: str, network: str, rate: Decimal, margin: Decimal) -> str:
    final_rate = rate * (1 + margin / 100)
    return f"""
{Emoji.BUY} <b>Beli {coin} ({network})</b>

{Emoji.CHART} Rate: <b>{format_currency(final_rate)}</b> / {coin}
{Emoji.INFO} Termasuk margin {margin}%

Masukkan jumlah dalam <b>IDR</b> yang ingin Anda belikan:
<i>Contoh: 100000</i>
"""


def format_buy_confirm(
    coin: str,
    network: str,
    fiat_amount: Decimal,
    crypto_amount: Decimal,
    rate: Decimal,
    network_fee: Decimal,
    total: Decimal
) -> str:
    network_fee_idr = network_fee * rate if network_fee > 0 else Decimal("0")
    return f"""
{Emoji.BUY} <b>Konfirmasi Pembelian</b>

{Emoji.CRYPTO} Coin: <b>{coin}</b> ({network})
{Emoji.MONEY} Jumlah Beli: <b>{format_currency(fiat_amount)}</b>
{Emoji.CHART} Rate: <b>{format_currency(rate)}</b> per {coin}
{Emoji.MONEY} Network Fee: <b>{format_currency(network_fee, coin)}</b> (~{format_currency(network_fee_idr)})

{Emoji.SUCCESS} Anda akan menerima: <b>{format_currency(crypto_amount, coin)}</b>
{Emoji.WALLET} Total dipotong dari saldo: <b>{format_currency(total)}</b>

Konfirmasi pembelian?
"""


def format_sell_confirm(
    coin: str,
    network: str,
    crypto_amount: Decimal,
    fiat_amount: Decimal,
    rate: Decimal,
    deposit_address: str
) -> str:
    return f"""
{Emoji.SELL} <b>Konfirmasi Penjualan</b>

{Emoji.CRYPTO} Coin: <b>{coin}</b> ({network})
{Emoji.MONEY} Jumlah Jual: <b>{format_currency(crypto_amount, coin)}</b>
{Emoji.CHART} Rate: <b>{format_currency(rate)}</b> per {coin}

{Emoji.SUCCESS} Saldo akan bertambah: <b>{format_currency(fiat_amount)}</b>

{Emoji.WALLET} Kirim <b>{format_currency(crypto_amount, coin)}</b> ke alamat ini:
<code>{deposit_address}</code>

{Emoji.WARNING} Pastikan network yang digunakan: <b>{network}</b>
{Emoji.CLOCK} Saldo akan masuk setelah konfirmasi blockchain.
"""


def format_topup_menu() -> str:
    return f"""
{Emoji.TOPUP} <b>Deposit Saldo</b>

Pilih metode pembayaran:
"""


def format_topup_amount(method: str) -> str:
    return f"""
{Emoji.TOPUP} <b>Top Up via {method}</b>

Masukkan jumlah yang ingin di top up (dalam IDR):
<i>Minimum: Rp 10.000</i>
"""


def format_topup_instruction(
    method: str,
    account_no: str,
    account_name: str,
    amount: Decimal
) -> str:
    return f"""
{Emoji.BANK} <b>Instruksi Pembayaran</b>

Transfer ke:
{Emoji.CHECK} <b>{method}</b>
{Emoji.CHECK} No. Rekening: <code>{account_no}</code>
{Emoji.CHECK} Atas Nama: <b>{account_name}</b>
{Emoji.CHECK} Jumlah: <b>{format_currency(amount)}</b>

{Emoji.WARNING} Transfer dengan jumlah yang TEPAT.
{Emoji.INFO} Setelah transfer, klik "Konfirmasi Pembayaran".
"""


def format_withdraw_menu() -> str:
    return f"""
{Emoji.WITHDRAW} <b>Withdraw Saldo</b>

Pilih metode withdraw:
"""


def format_transaction_success(tx_type: str, amount: Decimal) -> str:
    return f"""
{Emoji.SUCCESS} <b>Transaksi Berhasil!</b>

{Emoji.CHECK} {tx_type}: <b>{format_currency(amount)}</b>

Terima kasih telah menggunakan layanan kami!
"""


def format_transaction_pending() -> str:
    return f"""
{Emoji.PENDING} <b>Menunggu Konfirmasi</b>

Transaksi Anda sedang diproses.
Kami akan mengirim notifikasi setelah dikonfirmasi.
"""


def format_error(message: str) -> str:
    return f"""
{Emoji.ERROR} <b>Error</b>

{message}

Silakan coba lagi atau hubungi support.
"""


def format_insufficient_balance(required: Decimal, current: Decimal) -> str:
    return f"""
{Emoji.ERROR} <b>Saldo Tidak Cukup</b>

{Emoji.MONEY} Dibutuhkan: <b>{format_currency(required)}</b>
{Emoji.WALLET} Saldo Anda: <b>{format_currency(current)}</b>

Silakan top up terlebih dahulu.
"""


def format_history_item(
    tx_type: str,
    amount: Decimal,
    status: str,
    created_at: str,
    coin: Optional[str] = None
) -> str:
    status_emoji = {
        "PENDING": Emoji.PENDING,
        "PROCESSING": Emoji.PROCESSING,
        "COMPLETED": Emoji.SUCCESS,
        "FAILED": Emoji.ERROR,
        "CANCELLED": Emoji.ERROR,
    }.get(status, Emoji.INFO)
    
    coin_str = f" ({coin})" if coin else ""
    
    return f"{status_emoji} {tx_type}{coin_str}: {format_currency(amount)} - {created_at}"


def format_referral_info(code: str, count: int, bonus_earned: Decimal) -> str:
    return f"""
{Emoji.REFERRAL} <b>Program Referral</b>

{Emoji.STAR} Kode Anda: <code>{code}</code>
{Emoji.USER} Total Referral: <b>{count}</b>
{Emoji.MONEY} Bonus Diperoleh: <b>{format_currency(bonus_earned)}</b>

Bagikan kode referral Anda dan dapatkan bonus untuk setiap teman yang bergabung!
"""
