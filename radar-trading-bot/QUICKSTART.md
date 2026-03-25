# Radar Trading Bot - QUICK START

## 🚀 Langkah 1: Install

```bash
cd /root/.openclaw/workspace/radar-trading-bot
pip install -r requirements.txt
```

## ⚙️ Langkah 2: Setup Config

```bash
cp config/config.example.json config/config.json
nano config/config.json
```

Isi API key lu:
```json
{
  "api_key": "BINANCE_API_KEY_LU",
  "api_secret": "BINANCE_SECRET_LU", 
  "testnet": true,
  "symbols": ["BTCUSDT"],
  "check_interval_minutes": 5,
  "risk_per_trade_usd": 0.5,
  "max_leverage": 20
}
```

## 🧪 Langkah 3: Test

```bash
python3 test_setup.py
```

Kalo semua ✅, lanjut!

## ▶️ Langkah 4: Run (Testnet dulu!)

```bash
python3 bot.py
```

## 🚨 Emergency Stop

Kalo perlu stop SEMUA:
```bash
python3 emergency_stop.py
```

## 📊 Monitor

```bash
# Lihat log
tail -f logs/trading_*.log

# Cek posisi
python3 -c "
import json
from binance.client import Client
with open('config/config.json') as f:
    c = json.load(f)
client = Client(c['api_key'], c['api_secret'], testnet=c['testnet'])
pos = client.futures_position_information()
for p in pos:
    if float(p['positionAmt']) != 0:
        print(f\"{p['symbol']}: {p['positionAmt']} @ {p['entryPrice']}\")
"
```

## ⚡ Auto Start (Optional)

```bash
# Copy service file
sudo cp radar-bot.service /etc/systemd/system/
sudo systemctl daemon-reload

# Start
sudo systemctl start radar-bot

# Auto-run on boot
sudo systemctl enable radar-bot

# Cek status
sudo systemctl status radar-bot
```

## 🔑 API Key Setup

1. Login https://testnet.binancefuture.com (untuk test)
2. Profile → API Management
3. Create API Key
4. Whitelist IP: **46.224.175.81**
5. Copy key & secret ke config.json

## ✅ Checklist Sebelum Live

- [ ] Testnet berjalan lancar
- [ ] Beberapa trade sukses di testnet
- [ ] Paham emergency stop
- [ ] Sudah deposit USDT
- [ ] Ganti `testnet: false` di config
- [ ] Ready monitoring

## 💰 Risk Settings

**DEFAULT: $0.5 per trade** (udah di-set)

Gak bisa diubah dari bot. Kalo mau ganti, edit `config.json` tapi **ATURAN LU $0.5!**

## 📞 Troubleshooting

| Problem | Solusi |
|---------|--------|
| Config not found | `cp config/config.example.json config/config.json` |
| Invalid API key | Cek key & IP whitelist |
| No module | `pip install -r requirements.txt` |
| Low balance | Deposit USDT ke Futures |
| Connection error | Cek internet & API key |

## 🎯 Rules

1. **Risk fix $0.5** - Gak boleh lebih
2. **R:R >= 2** - Target min 2x risk
3. **Testnet dulu** - Jangan langsung live
4. **Monitor awal** - Cek bot jalan bener gak
5. **Emergency ready** - Siap stop kapan aja

---

**Siap trading!** 🚀💀
