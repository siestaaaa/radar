# 🤖 Radar Trading Bot

Auto-execute trading bot menggunakan ICT Framework dengan **RISK FIX $0.5 per trade**.

## ⚠️ PERINGATAN

- **Testnet dulu sebelum live!**
- Bot auto-execute, pastikan rule sudah benar
- Monitor terus di awal
- Siapkan cut-off manual kalo perlu

## 📁 Structure

```
radar-trading-bot/
├── bot.py              # Main bot
├── config/
│   └── config.json     # API keys & settings
├── logs/               # Trade logs
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## 🚀 Setup

### 1. Install Dependencies

```bash
cd radar-trading-bot
pip install -r requirements.txt
```

### 2. Setup Config

```bash
cp config/config.example.json config/config.json
nano config/config.json
```

Edit config.json:
```json
{
  "api_key": "your_binance_api_key",
  "api_secret": "your_binance_secret",
  "testnet": true,           // <-- TRUE dulu!
  "symbols": ["BTCUSDT"],
  "check_interval_minutes": 5,
  "risk_per_trade_usd": 0.5,  // <-- FIX $0.5
  "max_leverage": 20
}
```

### 3. Get Binance API Keys

1. Login https://testnet.binancefuture.com (untuk test)
2. Atau https://www.binance.com (untuk live)
3. Profile → API Management
4. Create API Key
5. Whitelist IP: `46.224.175.81`

### 4. Test Run (Testnet)

```bash
python3 bot.py
```

Kalo jalan, bakal muncul:
```
RADAR BOT STARTED
Risk: $0.5/trade
Testnet: True
```

### 5. Live Trading

Kalo testnet sudah OK:

1. Ganti `testnet: false` di config.json
2. Pastikan ada deposit USDT di Futures
3. Run lagi

## 📊 Logic Bot

### Entry Rules
1. **Breakout**: Close above/below recent high/low
2. **R:R >= 2**: Target minimum 2x risk
3. **No position**: Skip kalo udah ada posisi

### Risk Management
- **Fixed Risk**: $0.5 per trade (gak boleh lebih!)
- **Auto Leverage**: Kalkulasi otomatis
- **SL/TP**: Set otomatis pas entry

### Exit
- Stop Loss: Beyond recent swing
- Take Profit: 2R minimum

## 🛡️ Safety Features

- ✅ Testnet mode default
- ✅ Fixed risk validation
- ✅ Check existing positions
- ✅ Min balance check
- ✅ Error handling & recovery

## 📈 Monitor

### Check Logs
```bash
tail -f logs/trading_YYYYMMDD.log
```

### Check Balance
```bash
python3 -c "
import json
from binance.client import Client
with open('config/config.json') as f:
    c = json.load(f)
client = Client(c['api_key'], c['api_secret'], testnet=c['testnet'])
acc = client.futures_account()
for a in acc['assets']:
    if a['asset'] == 'USDT':
        print(f\"Balance: {a['availableBalance']} USDT\")
"
```

### Stop Bot
```bash
Ctrl+C
```

## 🔧 Troubleshooting

### "Config not found"
```bash
cp config/config.example.json config/config.json
```

### "Invalid API Key"
- Cek key bener gak
- Cek IP whitelist
- Cek testnet vs live

### "Insufficient balance"
- Deposit USDT ke Futures wallet
- Min balance: $10 recommended

## ⚡ Advanced

### Tambah Symbol
Edit `config.json`:
```json
"symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
```

### Ganti Interval
```json
"check_interval_minutes": 15  // Cek tiap 15 menit
```

### Multiple Timeframes
Edit `bot.py`, ganti interval di `check_signal()`.

## 📝 Log Format

```
2024-03-24 19:30:00 - INFO - RADAR BOT STARTED
2024-03-24 19:30:01 - INFO - Checking BTCUSDT...
2024-03-24 19:30:02 - INFO - Signal: BUY | R:R: 2.5
2024-03-24 19:30:03 - INFO - ✅ TRADE EXECUTED!
```

## 🆘 Emergency Stop

Kalo mau stop SEMUA posisi:
```python
from binance.client import Client
client = Client(api_key, api_secret)
positions = client.futures_position_information()
for pos in positions:
    if float(pos['positionAmt']) != 0:
        client.futures_create_order(
            symbol=pos['symbol'],
            side='SELL' if float(pos['positionAmt']) > 0 else 'BUY',
            type='MARKET',
            quantity=abs(float(pos['positionAmt']))
        )
```

## 💀 Disclaimer

Trading berisiko. Bot ini:
- Auto-execute tanpa konfirmasi
- Bisa loss
- Butuh monitoring

**JANGAN** trade dengan uang yang gak sanggup lu loss.

---

Dibuat dengan framework ICT Step 1-7
Risk: $0.5 fixed per trade 🔒
