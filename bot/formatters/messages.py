from decimal import Decimal
from typing import Optional


class Emoji:
    CHECK = "✓"
    CROSS = "✗"
    ARROW = "→"
    DOT = "•"
    DIVIDER = "─"


def format_currency(amount: Decimal, symbol: str = "IDR") -> str:
    if symbol == "IDR":
        return f"Rp {amount:,.0f}"
    return f"{amount:,.8f}".rstrip('0').rstrip('.') + f" {symbol}"


def format_welcome() -> str:
    return """<b>Selamat Datang di KriptoEcer</b>

Platform jual beli crypto terpercaya.
{0} Transaksi cepat & aman
{0} Harga kompetitif  
{0} Support 24/7

Silakan daftar untuk mulai trading.""".format(Emoji.DOT)


def format_terms() -> str:
    return """<b>Syarat & Ketentuan</b>

Dengan menggunakan layanan ini, Anda menyetujui:

1. Anda berusia minimal 18 tahun
2. Data yang diberikan adalah valid
3. Anda bertanggung jawab atas keamanan akun
4. Transaksi bersifat final setelah dikonfirmasi
5. Kami berhak membekukan akun yang mencurigakan

Pastikan Anda memahami risiko trading crypto."""


def format_main_menu(balance: Decimal, name: str) -> str:
    return """<b>Menu Utama</b>

Halo, <b>{name}</b>
Saldo: <b>{balance}</b>

Pilih menu di bawah:""".format(name=name, balance=format_currency(balance))


def format_rates(rates: dict, usd_to_idr: Decimal) -> str:
    supported = ["BTC", "ETH", "BNB", "SOL", "USDT", "USDC"]
    
    lines = ["<b>Harga Crypto</b>\n"]
    
    for symbol in supported:
        if symbol in rates:
            price_usd = Decimal(str(rates[symbol]))
            price_idr = price_usd * usd_to_idr
            lines.append(f"{Emoji.DOT} <b>{symbol}</b>: {format_currency(price_idr)}")
    
    lines.append(f"\n<i>Rate: $1 = Rp {usd_to_idr:,.0f}</i>")
    
    return "\n".join(lines)


def format_balance(balance: Decimal) -> str:
    return """<b>Saldo Anda</b>

<b>{balance}</b>

{0} Deposit untuk menambah saldo
{0} Withdraw untuk menarik saldo""".format(Emoji.DOT, balance=format_currency(balance))


def format_signup_email() -> str:
    return """<b>Email</b>

Masukkan alamat email Anda yang aktif.

<i>Contoh: nama@email.com</i>"""


def format_signup_whatsapp() -> str:
    return """<b>Nomor WhatsApp</b>

Masukkan nomor WhatsApp Anda.

<i>Contoh: 081234567890</i>"""


def format_signup_location() -> str:
    return """<b>Lokasi</b>

Bagikan lokasi Anda untuk verifikasi.
Klik tombol di bawah untuk share lokasi."""


def format_signup_referral() -> str:
    return """<b>Kode Referral</b> (Opsional)

Jika punya kode referral dari teman, masukkan sekarang.

Atau klik "Lewati" untuk lanjut."""


def format_signup_success(referral_code: str) -> str:
    return """<b>Pendaftaran Berhasil</b> {check}

Akun Anda sudah aktif.

Kode referral Anda: <code>{code}</code>
Bagikan ke teman untuk dapat bonus!""".format(check=Emoji.CHECK, code=referral_code)


def format_buy_menu() -> str:
    return """<b>Beli Crypto</b>

Pilih cryptocurrency:"""


def format_sell_menu() -> str:
    return """<b>Jual Crypto</b>

Pilih cryptocurrency:"""


def format_coin_networks(coin: str) -> str:
    return """<b>Pilih Network {coin}</b>

Pilih network yang tersedia:""".format(coin=coin)


def format_buy_amount(coin: str, network: str, rate: Decimal, margin: Decimal) -> str:
    final_rate = rate * (1 + margin / 100)
    return """<b>Beli {coin}</b> ({network})

Rate: <b>{rate}</b> / {coin}
<i>Sudah termasuk margin {margin}%</i>

Masukkan jumlah dalam IDR:
<i>Min: Rp 10.000</i>""".format(
        coin=coin,
        network=network,
        rate=format_currency(final_rate),
        margin=margin
    )


def format_buy_confirm(
    coin: str,
    network: str,
    fiat_amount: Decimal,
    crypto_amount: Decimal,
    rate: Decimal,
    network_fee: Decimal,
    total: Decimal
) -> str:
    return """<b>Konfirmasi Pembelian</b>

{dot} Coin: <b>{coin}</b> ({network})
{dot} Jumlah: <b>{fiat}</b>
{dot} Rate: <b>{rate}</b>/{coin}
{dot} Fee: <b>{fee}</b>

{arrow} Anda terima: <b>{crypto}</b>
{arrow} Dipotong: <b>{total}</b>

Lanjutkan pembelian?""".format(
        dot=Emoji.DOT,
        arrow=Emoji.ARROW,
        coin=coin,
        network=network,
        fiat=format_currency(fiat_amount),
        rate=format_currency(rate),
        fee=format_currency(network_fee, coin),
        crypto=format_currency(crypto_amount, coin),
        total=format_currency(total)
    )


def format_sell_confirm(
    coin: str,
    network: str,
    crypto_amount: Decimal,
    fiat_amount: Decimal,
    rate: Decimal,
    deposit_address: str
) -> str:
    return """<b>Konfirmasi Penjualan</b>

{dot} Coin: <b>{coin}</b> ({network})
{dot} Jumlah: <b>{crypto}</b>
{dot} Rate: <b>{rate}</b>/{coin}

{arrow} Saldo bertambah: <b>{fiat}</b>

Kirim <b>{crypto}</b> ke:
<code>{address}</code>

<i>Pastikan network: {network}</i>""".format(
        dot=Emoji.DOT,
        arrow=Emoji.ARROW,
        coin=coin,
        network=network,
        crypto=format_currency(crypto_amount, coin),
        rate=format_currency(rate),
        fiat=format_currency(fiat_amount),
        address=deposit_address
    )


def format_topup_menu() -> str:
    return """<b>Deposit Saldo</b>

Pilih metode pembayaran:"""


def format_topup_amount(method: str) -> str:
    return """<b>Deposit via {method}</b>

Masukkan jumlah (IDR):
<i>Min: Rp 10.000</i>""".format(method=method)


def format_topup_instruction(
    method: str,
    account_no: str,
    account_name: str,
    amount: Decimal
) -> str:
    return """<b>Instruksi Pembayaran</b>

Transfer ke:
{dot} <b>{method}</b>
{dot} No. Rek: <code>{account_no}</code>
{dot} Nama: <b>{account_name}</b>
{dot} Jumlah: <b>{amount}</b>

<i>Transfer dengan jumlah TEPAT</i>""".format(
        dot=Emoji.DOT,
        method=method,
        account_no=account_no,
        account_name=account_name,
        amount=format_currency(amount)
    )


def format_withdraw_menu() -> str:
    return """<b>Withdraw Saldo</b>

Pilih metode:"""


def format_transaction_success(tx_type: str, amount: Decimal) -> str:
    return """<b>Transaksi Berhasil</b> {check}

{tx_type}: <b>{amount}</b>""".format(
        check=Emoji.CHECK,
        tx_type=tx_type,
        amount=format_currency(amount)
    )


def format_transaction_pending() -> str:
    return """<b>Menunggu Konfirmasi</b>

Transaksi sedang diproses.
Anda akan menerima notifikasi setelah dikonfirmasi."""


def format_error(message: str) -> str:
    return """<b>Error</b> {cross}

{message}""".format(cross=Emoji.CROSS, message=message)


def format_insufficient_balance(required: Decimal, current: Decimal) -> str:
    return """<b>Saldo Tidak Cukup</b>

Dibutuhkan: <b>{required}</b>
Saldo Anda: <b>{current}</b>

Silakan deposit terlebih dahulu.""".format(
        required=format_currency(required),
        current=format_currency(current)
    )


def format_history_item(
    tx_type: str,
    amount: Decimal,
    status: str,
    created_at: str,
    coin: Optional[str] = None
) -> str:
    status_symbol = {
        "PENDING": "○",
        "PROCESSING": "◐",
        "COMPLETED": Emoji.CHECK,
        "FAILED": Emoji.CROSS,
        "CANCELLED": Emoji.CROSS,
    }.get(status, "○")
    
    coin_str = f" ({coin})" if coin else ""
    
    return f"{status_symbol} {tx_type}{coin_str}: {format_currency(amount)} - {created_at}"


def format_referral_info(code: str, count: int, bonus_earned: Decimal) -> str:
    return """<b>Program Referral</b>

Kode Anda: <code>{code}</code>
Total Referral: <b>{count}</b>
Bonus Diperoleh: <b>{bonus}</b>

Bagikan kode Anda dan dapatkan bonus!""".format(
        code=code,
        count=count,
        bonus=format_currency(bonus_earned)
    )
