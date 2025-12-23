# Deploy ke Vercel

## Metode 1: Via GitHub (Recommended)

### 1. Push ke GitHub
```bash
git add .
git commit -m "Deploy to Vercel"
git push origin main
```

### 2. Import di Vercel
1. Buka https://vercel.com/new
2. Pilih "Import Git Repository"
3. Pilih repo GitHub kamu
4. Klik "Import"

### 3. Setup Environment Variables
Di halaman configure project, tambahkan Environment Variables:

**WAJIB (untuk build):**
- `BOT_DATABASE` - PostgreSQL connection string (NeonSQL) - **HARUS ADA SAAT BUILD untuk prisma generate**

**WAJIB (untuk runtime):**
- `TELEGRAM_BOT_TOKEN` - Token dari @BotFather
- `CRYPTOBOT_API_TOKEN` - CryptoBot API token
- `ADMIN_TELEGRAM_IDS` - Comma-separated admin Telegram IDs

**OPSIONAL:**
- `OXAPAY_MERCHANT_API_KEY` - OxaPay merchant API key
- `OXAPAY_PAYOUT_API_KEY` - OxaPay payout API key
- `OXAPAY_WEBHOOK_SECRET` - OxaPay webhook secret

### 4. Deploy
Klik "Deploy" dan tunggu selesai.

### 5. Set Telegram Webhook
Setelah deploy, buka URL:
```
https://your-project.vercel.app/api/set-webhook
```

### 6. Auto Deploy
Setiap push ke GitHub akan otomatis deploy ke Vercel!

---

## Metode 2: Via Vercel CLI

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Login & Deploy
```bash
vercel login
vercel --prod
```

### 3. Setup Environment Variables
Buka https://vercel.com → Project Settings → Environment Variables

---

## Setelah Deploy

### Set Telegram Webhook
Buka URL ini untuk set webhook:
```
https://your-project.vercel.app/api/set-webhook
```

### Update OxaPay Webhook URL
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
