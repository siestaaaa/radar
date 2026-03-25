#!/usr/bin/env python3
"""
Radar Trading Bot - ICT Framework Auto-Execute
Risk: $0.5 fixed per trade
"""

import os
import sys
import time
import json
import logging
from datetime import datetime

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/trading_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class RadarBot:
    def __init__(self, config):
        self.config = config
        self.risk_per_trade = config.get('risk_per_trade_usd', 0.5)
        self.testnet = config.get('testnet', True)
        
        try:
            from binance.client import Client
            self.client = Client(
                config['api_key'], 
                config['api_secret'],
                testnet=self.testnet
            )
            logger.info(f"Bot initialized - Testnet: {self.testnet}")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise
    
    def get_balance(self):
        """Get USDT balance"""
        try:
            account = self.client.futures_account()
            for asset in account['assets']:
                if asset['asset'] == 'USDT':
                    return float(asset['availableBalance'])
            return 0
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0
    
    def calculate_position_size(self, entry, stop_loss, balance):
        """Calculate position size with $0.5 fixed risk"""
        risk_distance = abs(entry - stop_loss)
        
        if risk_distance == 0:
            logger.error("Entry and stop cannot be same!")
            return None
        
        # FIXED: $0.5 risk
        risk_amount = self.risk_per_trade
        
        # Position size = Risk / Distance
        position_size = risk_amount / risk_distance
        
        # Calculate leverage
        notional = position_size * entry
        margin = notional / balance if balance > 0 else notional
        
        leverage = 1
        if margin > 0:
            leverage = int(notional / (balance * 0.1))  # Use max 10% margin
            leverage = min(leverage, self.config.get('max_leverage', 20))
            leverage = max(leverage, 1)
        
        return {
            'size': round(position_size, 3),
            'leverage': leverage,
            'margin': round(notional / leverage, 2),
            'risk_usd': risk_amount
        }
    
    def check_signal(self, symbol):
        """Simple ICT signal check"""
        try:
            # Get recent candles
            klines = self.client.futures_klines(
                symbol=symbol,
                interval='15m',
                limit=50
            )
            
            if not klines:
                return None
            
            # Get last candle
            current = klines[-1]
            prev = klines[-2]
            
            current_close = float(current[4])
            prev_close = float(prev[4])
            current_high = float(current[2])
            current_low = float(current[3])
            
            # Simple breakout logic
            recent_high = max([float(k[2]) for k in klines[-10:-1]])
            recent_low = min([float(k[3]) for k in klines[-10:-1]])
            
            if current_close > recent_high and prev_close <= recent_high:
                return {
                    'type': 'BUY',
                    'entry': current_close,
                    'stop': recent_low,
                    'target': current_close + (current_close - recent_low) * 2
                }
            elif current_close < recent_low and prev_close >= recent_low:
                return {
                    'type': 'SELL',
                    'entry': current_close,
                    'stop': recent_high,
                    'target': current_close - (recent_high - current_close) * 2
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Signal check error: {e}")
            return None
    
    def execute_trade(self, symbol, signal):
        """Execute trade"""
        try:
            # Check existing positions
            positions = self.client.futures_position_information(symbol=symbol)
            for pos in positions:
                if float(pos['positionAmt']) != 0:
                    logger.info(f"Already in position for {symbol}")
                    return False
            
            # Get balance
            balance = self.get_balance()
            if balance < 10:
                logger.warning(f"Low balance: ${balance}")
                return False
            
            # Calculate position
            pos_data = self.calculate_position_size(
                signal['entry'],
                signal['stop'],
                balance
            )
            
            if not pos_data:
                return False
            
            logger.info(f"Position calc: {pos_data}")
            
            # Check R:R
            risk = abs(signal['entry'] - signal['stop'])
            reward = abs(signal['target'] - signal['entry'])
            rr = reward / risk if risk > 0 else 0
            
            if rr < 2:
                logger.info(f"R:R too low: {rr:.2f}")
                return False
            
            logger.info(f"Signal: {signal['type']} | R:R: {rr:.2f}")
            
            # Set leverage
            self.client.futures_change_leverage(
                symbol=symbol,
                leverage=pos_data['leverage']
            )
            
            # Determine side
            side = 'BUY' if signal['type'] == 'BUY' else 'SELL'
            opposite = 'SELL' if signal['type'] == 'BUY' else 'BUY'
            
            # Place market order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=pos_data['size']
            )
            
            logger.info(f"Order placed: {order['orderId']}")
            
            # Set stop loss
            self.client.futures_create_order(
                symbol=symbol,
                side=opposite,
                type='STOP_MARKET',
                stopPrice=round(signal['stop'], 2),
                quantity=pos_data['size']
            )
            
            # Set take profit
            self.client.futures_create_order(
                symbol=symbol,
                side=opposite,
                type='LIMIT',
                price=round(signal['target'], 2),
                quantity=pos_data['size'],
                timeInForce='GTC'
            )
            
            logger.info("✅ TRADE EXECUTED!")
            return True
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return False
    
    def run(self):
        """Main loop"""
        logger.info("="*50)
        logger.info("RADAR BOT STARTED")
        logger.info(f"Risk: ${self.risk_per_trade}/trade")
        logger.info(f"Testnet: {self.testnet}")
        logger.info(f"Symbols: {self.config['symbols']}")
        logger.info("="*50)
        
        while True:
            try:
                for symbol in self.config['symbols']:
                    logger.info(f"Checking {symbol}...")
                    
                    signal = self.check_signal(symbol)
                    if signal:
                        self.execute_trade(symbol, signal)
                    else:
                        logger.info("No signal")
                    
                    time.sleep(1)
                
                interval = self.config.get('check_interval_minutes', 5)
                logger.info(f"Sleeping {interval}min...")
                time.sleep(interval * 60)
                
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    # Load config
    config_path = 'config/config.json'
    
    if not os.path.exists(config_path):
        logger.error("Config not found!")
        logger.error("Copy config.example.json to config.json and edit")
        sys.exit(1)
    
    with open(config_path) as f:
        config = json.load(f)
    
    # Validate
    if 'YOUR_' in config['api_key']:
        logger.error("Please set your API keys in config.json!")
        sys.exit(1)
    
    # Run bot
    bot = RadarBot(config)
    bot.run()
