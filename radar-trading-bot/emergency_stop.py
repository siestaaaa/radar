#!/usr/bin/env python3
"""Emergency stop - Close all positions immediately"""

import json
import sys
from binance.client import Client

def emergency_stop():
    print("🚨 EMERGENCY STOP 🚨")
    print("Closing ALL positions...")
    
    with open('config/config.json') as f:
        config = json.load(f)
    
    client = Client(
        config['api_key'],
        config['api_secret'],
        testnet=config.get('testnet', True)
    )
    
    # Get all positions
    positions = client.futures_position_information()
    
    closed = 0
    for pos in positions:
        amt = float(pos['positionAmt'])
        if amt != 0:
            symbol = pos['symbol']
            side = 'SELL' if amt > 0 else 'BUY'
            
            try:
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=abs(amt),
                    reduceOnly=True
                )
                print(f"✅ Closed {symbol}: {amt}")
                closed += 1
            except Exception as e:
                print(f"❌ Failed {symbol}: {e}")
    
    if closed == 0:
        print("No open positions")
    else:
        print(f"\nClosed {closed} positions")
    
    # Cancel all orders
    print("\nCanceling all orders...")
    for pos in positions:
        try:
            client.futures_cancel_all_open_orders(symbol=pos['symbol'])
            print(f"✅ Canceled orders for {pos['symbol']}")
        except:
            pass
    
    print("\n✅ EMERGENCY STOP COMPLETE")

if __name__ == "__main__":
    confirm = input("Close ALL positions? (yes/no): ")
    if confirm.lower() == 'yes':
        emergency_stop()
    else:
        print("Cancelled")
