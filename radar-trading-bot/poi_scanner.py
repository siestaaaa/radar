#!/usr/bin/env python3
"""
Radar POI Scanner - Standalone Python Script
Auto-detect Points of Interest (POI) on 4H & 1H timeframes
NO AI API - Pure technical analysis
Sends alerts when POI detected
"""

import requests
import json
import time
import os
from datetime import datetime

class BinancePOIScanner:
    def __init__(self):
        self.base_url = "https://fapi.binance.com"
        self.symbol = "BTCUSDT"
        self.alert_log = "logs/poi_alerts.log"
        os.makedirs("logs", exist_ok=True)
        
    def log_alert(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.alert_log, "a") as f:
            f.write(log_msg + "\n")
    
    def fetch_klines(self, symbol, interval, limit=100):
        url = f"{self.base_url}/fapi/v1/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []
    
    def detect_fvg(self, candles):
        fvgs = []
        for i in range(len(candles) - 3):
            c1_low = float(candles[i][3])
            c1_high = float(candles[i][2])
            c3_high = float(candles[i+2][2])
            c3_low = float(candles[i+2][3])
            c1_time = candles[i][0]
            
            if c1_low > c3_high:
                fvgs.append({
                    "type": "BULLISH",
                    "top": c1_low,
                    "bottom": c3_high,
                    "ce_50": (c1_low + c3_high) / 2,
                    "formed_at": datetime.fromtimestamp(c1_time/1000).strftime("%Y-%m-%d %H:%M")
                })
            elif c1_high < c3_low:
                fvgs.append({
                    "type": "BEARISH",
                    "top": c3_low,
                    "bottom": c1_high,
                    "ce_50": (c1_high + c3_low) / 2,
                    "formed_at": datetime.fromtimestamp(c1_time/1000).strftime("%Y-%m-%d %H:%M")
                })
        return fvgs
    
    def detect_liquidity(self, candles):
        highs = [float(c[2]) for c in candles]
        lows = [float(c[3]) for c in candles]
        closes = [float(c[4]) for c in candles]
        
        return {
            "current_price": closes[-1],
            "recent_high": max(highs[-20:]),
            "recent_low": min(lows[-20:]),
            "swing_high": max(highs[-50:]),
            "swing_low": min(lows[-50:]),
            "pdh": max(highs[-24:]) if len(highs) >= 24 else max(highs),
            "pdl": min(lows[-24:]) if len(lows) >= 24 else min(lows)
        }
    
    def detect_order_blocks(self, candles):
        obs = []
        for i in range(len(candles) - 5):
            c_open = float(candles[i][1])
            c_high = float(candles[i][2])
            c_low = float(candles[i][3])
            c_close = float(candles[i][4])
            c_time = candles[i][0]
            future_close = float(candles[i+3][4])
            price_change = abs(future_close - c_close) / c_close
            
            if c_close < c_open and price_change > 0.01:
                if future_close > c_close * 1.02:
                    obs.append({
                        "type": "BULLISH",
                        "top": c_high,
                        "bottom": c_low,
                        "ce_50": (c_high + c_low) / 2,
                        "formed_at": datetime.fromtimestamp(c_time/1000).strftime("%Y-%m-%d %H:%M")
                    })
            elif c_close > c_open and price_change > 0.01:
                if future_close < c_close * 0.98:
                    obs.append({
                        "type": "BEARISH",
                        "top": c_high,
                        "bottom": c_low,
                        "ce_50": (c_high + c_low) / 2,
                        "formed_at": datetime.fromtimestamp(c_time/1000).strftime("%Y-%m-%d %H:%M")
                    })
        return obs
    
    def calculate_distance(self, poi, current_price):
        target = poi.get("ce_50", current_price)
        return abs(target - current_price) / current_price * 100
    
    def scan_timeframe(self, symbol, timeframe):
        print(f"\n🔍 Scanning {symbol} {timeframe}...")
        candles = self.fetch_klines(symbol, timeframe)
        if not candles:
            return {}
        current_price = float(candles[-1][4])
        return {
            "timeframe": timeframe,
            "current_price": current_price,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fvg": self.detect_fvg(candles),
            "liquidity": self.detect_liquidity(candles),
            "order_blocks": self.detect_order_blocks(candles)
        }
    
    def generate_alert(self, poi_4h, poi_1h):
        alerts = []
        current_price = poi_4h.get("current_price", 0)
        
        if poi_4h:
            for fvg in poi_4h.get("fvg", [])[:2]:
                dist = self.calculate_distance(fvg, current_price)
                if dist < 1.0:
                    alerts.append(f"🎯 4H FVG {fvg['type']}: {fvg['ce_50']:.2f} (CE 50%, {dist:.2f}% away)")
            
            liq = poi_4h.get("liquidity", {})
            if liq:
                dist_high = abs(liq['recent_high'] - current_price) / current_price * 100
                dist_low = abs(liq['recent_low'] - current_price) / current_price * 100
                if dist_high < 1.0:
                    alerts.append(f"🏔️ 4H Liquidity High: {liq['recent_high']:.2f} ({dist_high:.2f}%)")
                if dist_low < 1.0:
                    alerts.append(f"🏔️ 4H Liquidity Low: {liq['recent_low']:.2f} ({dist_low:.2f}%)")
            
            for ob in poi_4h.get("order_blocks", [])[:1]:
                dist = self.calculate_distance(ob, current_price)
                if dist < 2.0:
                    alerts.append(f"📦 4H OB {ob['type']}: {ob['ce_50']:.2f} ({dist:.2f}% away)")
        
        if poi_1h:
            for fvg in poi_1h.get("fvg", [])[:2]:
                dist = self.calculate_distance(fvg, current_price)
                if dist < 0.5:
                    alerts.append(f"🎯 1H FVG {fvg['type']}: {fvg['ce_50']:.2f} (CE 50%, {dist:.2f}% away)")
            
            if poi_4h.get("fvg") and poi_1h.get("fvg"):
                fvg_4h = poi_4h["fvg"][0] if poi_4h["fvg"] else None
                fvg_1h = poi_1h["fvg"][0] if poi_1h["fvg"] else None
                if fvg_4h and fvg_1h and fvg_4h["type"] == fvg_1h["type"]:
                    alerts.append(f"⚡ CONFLUENCE: 4H & 1H FVG aligned {fvg_4h['type']}")
        
        return "\n".join(alerts) if alerts else None
    
    def run_scan(self):
        print("="*60)
        print("🔍 RADAR POI SCANNER STARTED")
        print("Timeframes: 4H & 1H | Symbol: BTCUSDT")
        print("NO AI API - Pure Technical Analysis")
        print("="*60)
        
        while True:
            try:
                poi_4h = self.scan_timeframe("BTCUSDT", "4h")
                poi_1h = self.scan_timeframe("BTCUSDT", "1h")
                
                alert = self.generate_alert(poi_4h, poi_1h)
                
                if alert:
                    self.log_alert("\n" + "="*60)
                    self.log_alert("🚨 POI ALERT DETECTED!")
                    self.log_alert("="*60)
                    self.log_alert(alert)
                    self.log_alert(f"Current Price: {poi_4h['current_price']:.2f}")
                    self.log_alert("="*60)
                else:
                    print(f"✓ No POI - Price: {poi_4h['current_price']:.2f}")
                
                print(f"\n⏰ Next scan: 30 min | Last: {datetime.now().strftime('%H:%M')}\n")
                time.sleep(30 * 60)
                
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    scanner = BinancePOIScanner()
    scanner.run_scan()
