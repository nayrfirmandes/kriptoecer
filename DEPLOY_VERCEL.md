# Deploy ke Vercel

## Langkah-langkah

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Login ke Vercel
```bash
vercel login
```

### 3. Setup Environment Variables di Vercel
Buka https://vercel.com → Project Settings → Environment Variables

Tambahkan:
- `TELEGRAM_BOT_TOKEN` - Token dari @BotFather
- `BOT_DATABASE` - PostgreSQL connection string (NeonSQL)
- `OXAPAY_MERCHANT_API_KEY` - OxaPay merchant API key
- `OXAPAY_PAYOUT_API_KEY` - OxaPay payout API key
- `OXAPAY_WEBHOOK_SECRET` - OxaPay webhook secret
- `CRYPTOBOT_API_TOKEN` - CryptoBot API token
- `ADMIN_TELEGRAM_IDS` - Comma-separated admin Telegram IDs

### 4. Deploy
```bash
vercel --prod
```

### 5. Set Telegram Webhook
Setelah deploy, buka URL:
```
https://your-project.vercel.app/api/set-webhook
```

Ini akan otomatis set webhook Telegram ke Vercel.

### 6. Update OxaPay Webhook URL
Di dashboard OxaPay, set webhook URL ke:
```
https://your-project.vercel.app/webhook/oxapay
```

## Struktur Files

```
api/
├── telegram.py      # Telegram webhook handler
├── oxapay.py        # OxaPay webhook handler
└── set_webhook.py   # Set Telegram webhook
```

## Notes

- Vercel menggunakan serverless functions
- Setiap request timeout 10 detik (default)
- Database harus menggunakan connection pooling (NeonSQL sudah support)
