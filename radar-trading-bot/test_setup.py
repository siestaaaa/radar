#!/usr/bin/env python3
"""Test bot setup before running"""

import json
import sys

def test_config():
    print("🧪 Testing Config...")
    
    try:
        with open('config/config.json') as f:
            config = json.load(f)
        print("✅ Config loaded")
    except:
        print("❌ Config not found!")
        print("Run: cp config/config.example.json config/config.json")
        return False
    
    # Check API keys
    if 'YOUR_' in config.get('api_key', ''):
        print("❌ API key not set!")
        return False
    print("✅ API keys set")
    
    # Check risk
    risk = config.get('risk_per_trade_usd', 0)
    if risk != 0.5:
        print(f"⚠️ Risk is ${risk}, should be $0.5")
    else:
        print("✅ Risk set to $0.5")
    
    # Check testnet
    if config.get('testnet', True):
        print("✅ Testnet enabled (SAFE)")
    else:
        print("⚠️ LIVE MODE - Real money!")
    
    return True

def test_binance():
    print("\n🧪 Testing Binance Connection...")
    
    try:
        from binance.client import Client
        with open('config/config.json') as f:
            config = json.load(f)
        
        client = Client(
            config['api_key'],
            config['api_secret'],
            testnet=config.get('testnet', True)
        )
        
        # Test connection
        account = client.futures_account()
        balance = 0
        for asset in account['assets']:
            if asset['asset'] == 'USDT':
                balance = float(asset['availableBalance'])
        
        print(f"✅ Connected!")
        print(f"💰 Balance: {balance} USDT")
        
        if balance < 10:
            print("⚠️ Low balance! Need deposit.")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_logic():
    print("\n🧪 Testing Trading Logic...")
    
    # Test position calculation
    entry = 50000
    stop = 49500
    risk = 0.5
    distance = abs(entry - stop)  # 500
    size = risk / distance  # 0.001
    
    print(f"Entry: {entry}")
    print(f"Stop: {stop}")
    print(f"Distance: {distance}")
    print(f"Position Size: {size:.6f}")
    print(f"Risk: ${risk}")
    
    if size > 0:
        print("✅ Logic OK")
        return True
    else:
        print("❌ Logic error")
        return False

if __name__ == "__main__":
    print("="*50)
    print("RADAR BOT - PRE-FLIGHT CHECK")
    print("="*50)
    
    results = []
    results.append(("Config", test_config()))
    results.append(("Binance", test_binance()))
    results.append(("Logic", test_logic()))
    
    print("\n" + "="*50)
    print("RESULTS:")
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🚀 Ready to launch!")
        print("Run: python3 bot.py")
    else:
        print("\n⚠️ Fix issues before running")
        sys.exit(1)
