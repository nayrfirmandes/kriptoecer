# Crypto Trading Telegram Bot

## Overview
Telegram bot untuk jual beli cryptocurrency dengan sistem saldo internal. Bot ini terintegrasi dengan OxaPay untuk transaksi crypto.

## Tech Stack
- **Bot**: Python 3.11 + Aiogram 3.x
- **Database**: PostgreSQL (NeonSQL)
- **ORM**: Prisma
- **Admin Panel**: Next.js (planned)

## Project Structure
```
bot/
├── main.py              # Entry point
├── config.py            # Environment config
├── webhook.py           # OxaPay webhook handler
├── handlers/            # Telegram handlers
│   ├── start.py         # /start command
│   ├── signup.py        # Registration flow
│   ├── menu.py          # Main menu
│   ├── balance.py       # Balance view
│   ├── topup.py         # Top up flow
│   ├── withdraw.py      # Withdraw flow
│   ├── buy.py           # Buy crypto flow
│   ├── sell.py          # Sell crypto flow
│   ├── history.py       # Transaction history
│   └── admin.py         # Admin commands
├── services/            # Business logic
│   └── oxapay.py        # OxaPay API wrapper
├── keyboards/           # InlineKeyboard builders
│   └── inline.py        # All keyboards
├── formatters/          # Message formatters + emoji
│   └── messages.py      # All messages
├── middlewares/         # Aiogram middlewares
│   ├── throttling.py    # Rate limiting
│   ├── database.py      # DB injection
│   ├── user_status.py   # User status check
│   └── logging.py       # Request logging
├── db/                  # Database queries
│   └── queries.py       # All DB operations
└── utils/               # Helpers
    └── helpers.py       # Utility functions

prisma/
└── schema.prisma        # Database schema

admin-panel/             # Next.js admin (planned)
```

## Environment Variables
Required secrets:
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `DATABASE_URL` - NeonSQL connection string
- `OXAPAY_API_KEY` - OxaPay API key
- `OXAPAY_MERCHANT_ID` - OxaPay merchant ID
- `OXAPAY_WEBHOOK_SECRET` - Webhook verification secret
- `ADMIN_TELEGRAM_IDS` - Comma-separated admin Telegram IDs

## Features
- User registration with email, WhatsApp, location
- Referral system with bonus
- Balance management (top up, withdraw)
- Buy crypto (BTC, ETH, BNB, SOL, USDT, USDC)
- Sell crypto with deposit address
- Transaction history
- Admin commands for approving transactions
- Rate limiting (100-300ms response time target)
- User inactive detection (6 months)

## Running the Bot
```bash
python run_bot.py
```

## Database Commands
```bash
# Generate Prisma client
prisma generate

# Push schema to database
prisma db push

# Open Prisma Studio
prisma studio
```

## Admin Commands (Telegram)
- `/admin` - Admin dashboard
- `/pending_topup` - View pending top ups
- `/pending_withdraw` - View pending withdrawals
- `/approve_topup [id]` - Approve top up
- `/reject_topup [id]` - Reject top up
- `/approve_withdraw [id]` - Approve withdrawal
- `/reject_withdraw [id]` - Reject withdrawal

## Deployment

### Vercel
Lihat `DEPLOY_VERCEL.md` untuk panduan lengkap.

Files deployment:
```
api/
├── telegram.py      # Telegram webhook handler
├── oxapay.py        # OxaPay webhook handler
└── set_webhook.py   # Set Telegram webhook
vercel.json          # Vercel config
```

### Environment Variables
Semua config menggunakan `.env` file:
- `TELEGRAM_BOT_TOKEN`
- `BOT_DATABASE`
- `OXAPAY_MERCHANT_API_KEY`
- `OXAPAY_PAYOUT_API_KEY`
- `OXAPAY_WEBHOOK_SECRET`
- `CRYPTOBOT_API_TOKEN`
- `ADMIN_TELEGRAM_IDS`

## Recent Changes
- CryptoBot integration untuk deposit crypto (USDT/USDC) dengan margin 5%
- Real-time rate dari CryptoBot API
- Vercel deployment setup
- Initial setup with all handlers
- Prisma schema with all models
- OxaPay integration for payments
- Webhook endpoint for crypto confirmations
