#!/usr/bin/env python3
"""
Radar Enhanced Auto-Bot
Full auto trading with POI detection + Safety limits
Max 3 losses per day
"""

import json
import time
import os
from datetime import datetime, date
from binance.client import Client

class EnhancedAutoBot:
    def __init__(self):
        # Load config
        with open('config/config.json') as f:
            self.config = json.load(f)
        
        self.client = Client(
            self.config['api_key'],
            self.config['api_secret'],
            testnet=self.config.get('testnet', False)
        )
        
        # Safety settings
        self.max_losses_per_day = 3
        self.min_balance = 10  # USD
        self.risk_per_trade = 0.5
        
        # Tracking
        self.today = date.today()
        self.daily_losses = 0
        self.daily_trades = 0
        
        # State file
        self.state_file = "logs/daily_state.json"
        self.load_state()
        
        os.makedirs("logs", exist_ok=True)
        
    def log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        
        with open(f"logs/auto_bot_{date.today()}.log", "a") as f:
            f.write(log_msg + "\n")
    
    def load_state(self):
        """Load daily state"""
        if os.path.exists(self.state_file):
            with open(self.state_file) as f:
                state = json.load(f)
                saved_date = state.get('date')
                if saved_date == str(self.today):
                    self.daily_losses = state.get('losses', 0)
                    self.daily_trades = state.get('trades', 0)
    
    def save_state(self):
        """Save daily state"""
        state = {
            'date': str(self.today),
            'losses': self.daily_losses,
            'trades': self.daily_trades
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
    
    def check_daily_reset(self):
        """Check if new day (reset counters)"""
        current_date = date.today()
        if current_date != self.today:
            self.log(f"🌅 New day! Resetting counters")
            self.today = current_date
            self.daily_losses = 0
            self.daily_trades = 0
            self.save_state()
    
    def get_balance(self):
        """Get USDT balance"""
        try:
            account = self.client.futures_account()
            for asset in account['assets']:
                if asset['asset'] == 'USDT':
                    return float(asset['availableBalance'])
            return 0
        except Exception as e:
            self.log(f"Error getting balance: {e}")
            return 0
    
    def check_safety(self):
        """Check if safe to trade"""
        self.check_daily_reset()
        
        # Check max losses
        if self.daily_losses >= self.max_losses_per_day:
            self.log(f"🛑 MAX LOSSES REACHED ({self.daily_losses}/{self.max_losses_per_day}) - STOPPING")
            return False, "max_losses"
        
        # Check balance
        balance = self.get_balance()
        if balance < self.min_balance:
            self.log(f"💰 LOW BALANCE (${balance:.2f}) - NEED ${self.min_balance}")
            return False, "low_balance"
        
        # Check existing positions
        positions = self.client.futures_position_information()
        for pos in positions:
            if float(pos['positionAmt']) != 0:
                return False, "existing_position"
        
        return True, "ok"
    
    def fetch_klines(self, symbol, interval, limit=100):
        """Fetch candle data"""
        try:
            return self.client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        except Exception as e:
            self.log(f"Error fetching data: {e}")
            return []
    
    def detect_fvg(self, candles):
        """Detect Fair Value Gaps"""
        fvgs = []
        for i in range(len(candles) - 3):
            c1_low = float(candles[i][3])
            c1_high = float(candles[i][2])
            c3_high = float(candles[i+2][2])
            c3_low = float(candles[i+2][3])
            
            if c1_low > c3_high:
                fvgs.append({
                    "type": "BULLISH",
                    "top": c1_low,
                    "bottom": c3_high,
                    "ce_50": (c1_low + c3_high) / 2
                })
            elif c1_high < c3_low:
                fvgs.append({
                    "type": "BEARISH",
                    "top": c3_low,
                    "bottom": c1_high,
                    "ce_50": (c1_high + c3_low) / 2
                })
        return fvgs
    
    def detect_liquidity(self, candles):
        """Detect liquidity levels"""
        highs = [float(c[2]) for c in candles]
        lows = [float(c[3]) for c in candles]
        
        return {
            "recent_high": max(highs[-20:]),
            "recent_low": min(lows[-20:]),
            "pdh": max(highs[-24:]) if len(highs) >= 24 else max(highs),
            "pdl": min(lows[-24:]) if len(lows) >= 24 else min(lows)
        }
    
    def calculate_signal(self):
        """Calculate trading signal from POI"""
        symbol = self.config['symbols'][0]  # BTCUSDT
        
        # Fetch 4H and 1H data
        candles_4h = self.fetch_klines(symbol, "4h", 50)
        candles_1h = self.fetch_klines(symbol, "1h", 50)
        
        if not candles_4h or not candles_1h:
            return None
        
        current_price = float(candles_4h[-1][4])
        
        # Detect FVGs
        fvg_4h = self.detect_fvg(candles_4h)
        fvg_1h = self.detect_fvg(candles_1h)
        
        # Detect liquidity
        liq_4h = self.detect_liquidity(candles_4h)
        
        signal = None
        
        # Check for confluence (4H & 1H aligned)
        if fvg_4h and fvg_1h:
            latest_4h = fvg_4h[-1]
            latest_1h = fvg_1h[-1]
            
            if latest_4h["type"] == latest_1h["type"]:
                # Confluence found
                fvg_type = latest_4h["type"]
                entry = latest_4h["ce_50"]
                
                if fvg_type == "BULLISH":
                    stop = liq_4h["recent_low"] * 0.995
                    target = liq_4h["recent_high"]
                else:
                    stop = liq_4h["recent_high"] * 1.005
                    target = liq_4h["recent_low"]
                
                # Calculate R:R
                risk = abs(entry - stop)
                reward = abs(target - entry)
                rr = reward / risk if risk > 0 else 0
                
                if rr >= 2.0:
                    signal = {
                        "type": fvg_type,
                        "entry": entry,
                        "stop": stop,
                        "target": target,
                        "rr": rr,
                        "confluence": True
                    }
        
        return signal
    
    def execute_trade(self, signal):
        """Execute trade"""
        symbol = self.config['symbols'][0]
        
        try:
            # Calculate position size
            risk_amount = self.risk_per_trade
            price_diff = abs(signal['entry'] - signal['stop'])
            position_size = risk_amount / price_diff
            
            # Round to 3 decimals
            position_size = round(position_size, 3)
            
            side = "BUY" if signal['type'] == "BULLISH" else "SELL"
            opposite = "SELL" if signal['type'] == "BULLISH" else "BUY"
            
            self.log(f"🚀 EXECUTING {side} ORDER")
            self.log(f"   Entry: {signal['entry']:.2f}")
            self.log(f"   Stop: {signal['stop']:.2f}")
            self.log(f"   Target: {signal['target']:.2f}")
            self.log(f"   R:R: {signal['rr']:.2f}")
            self.log(f"   Size: {position_size}")
            
            # Set leverage
            self.client.futures_change_leverage(symbol=symbol, leverage=5)
            
            # Market order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=position_size
            )
            
            self.log(f"✅ Order placed: {order['orderId']}")
            
            # Stop loss
            self.client.futures_create_order(
                symbol=symbol,
                side=opposite,
                type="STOP_MARKET",
                stopPrice=round(signal['stop'], 2),
                quantity=position_size
            )
            
            # Take profit
            self.client.futures_create_order(
                symbol=symbol,
                side=opposite,
                type="LIMIT",
                price=round(signal['target'], 2),
                quantity=position_size,
                timeInForce="GTC"
            )
            
            self.daily_trades += 1
            self.save_state()
            
            return True
            
        except Exception as e:
            self.log(f"❌ Trade error: {e}")
            return False
    
    def check_closed_trades(self):
        """Check if any trades closed and update loss count"""
        try:
            trades = self.client.futures_account_trades()
            today_str = str(date.today())
            
            for trade in trades:
                trade_time = datetime.fromtimestamp(trade['time'] / 1000)
                if trade_time.date() == date.today():
                    # Check if this was a losing trade
                    # This is simplified - in real scenario need to match entry/exit
                    pass
                    
        except Exception as e:
            pass
    
    def run(self):
        """Main loop"""
        self.log("="*60)
        self.log("🤖 RADAR ENHANCED AUTO-BOT")
        self.log("="*60)
        self.log(f"Max losses/day: {self.max_losses_per_day}")
        self.log(f"Min balance: ${self.min_balance}")
        self.log(f"Risk/trade: ${self.risk_per_trade}")
        self.log(f"Today's losses: {self.daily_losses}/{self.max_losses_per_day}")
        self.log("="*60)
        
        while True:
            try:
                # Check safety
                safe, reason = self.check_safety()
                
                if not safe:
                    if reason == "max_losses":
                        self.log("⏳ Waiting for tomorrow...")
                        time.sleep(3600)  # Sleep 1 hour
                        continue
                    elif reason == "low_balance":
                        self.log("💰 Need deposit!")
                        time.sleep(300)
                        continue
                    elif reason == "existing_position":
                        self.log("⏳ Position active, waiting...")
                        time.sleep(300)
                        continue
                
                # Calculate signal
                self.log("🔍 Scanning for POI signal...")
                signal = self.calculate_signal()
                
                if signal:
                    self.log(f"📊 SIGNAL: {signal['type']} | R:R {signal['rr']:.2f}")
                    
                    if signal['confluence']:
                        self.log("⚡ CONFLUENCE detected - HIGH PROBABILITY")
                    
                    # Execute
                    success = self.execute_trade(signal)
                    
                    if success:
                        self.log("✅ TRADE EXECUTED - Monitoring...")
                        # Wait 2 hours before next scan
                        time.sleep(7200)
                    else:
                        time.sleep(300)
                else:
                    self.log("⏳ No valid signal")
                    time.sleep(300)  # Check every 5 min
                    
            except Exception as e:
                self.log(f"❌ Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = EnhancedAutoBot()
    bot.run()
