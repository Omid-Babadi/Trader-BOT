import time
import json
from market import getPrice
from database.db import record_trade

TRADE_HISTORY_FILE = "trade_history.json"

def manage_trade(coin, buy_price, total_money, mode="default", profit_percent=1):
    """
    Monitors an open trade with support for aggressive mode.
    
    Args:
        coin: The cryptocurrency to trade
        buy_price: Entry price
        total_money: Total money available for trading
        mode: Trading mode ('default' or 'aggressive')
        profit_percent: Target profit percentage
    """
    if mode.lower() == "aggressive":
        return manage_aggressive_trade(coin, buy_price, total_money, profit_percent)
    else:
        return manage_default_trade(coin, buy_price, total_money, profit_percent)

def manage_default_trade(coin, buy_price, total_money, profit_percent):
    """Default trading mode - enters with full amount"""
    target_price = buy_price * (1 + (profit_percent / 100))
    last_profit_target = buy_price
    position_size = total_money / buy_price

    print(f"📈 Entering default trade with {position_size} {coin} at ${buy_price}")
    
    while True:
        current_price = getPrice(coin)

        if current_price >= target_price:
            last_profit_target = target_price
            target_price *= (1 + (profit_percent / 100))
            print(f"📈 New profit target: ${target_price}")

        elif current_price < last_profit_target:
            profit = (current_price - buy_price) * position_size
            print(f"✅ Taking profit: ${profit:.2f}")
            record_trade(coin, "sell", current_price, f"Default mode profit: ${profit:.2f}")
            return True

        time.sleep(10)

def manage_aggressive_trade(coin, buy_price, total_money, profit_percent):
    """Aggressive trading mode - enters in three parts"""
    initial_target = buy_price * (1 + (profit_percent / 100))
    second_target = initial_target * (1 + (profit_percent / 100))
    final_target = second_target * (1 + (profit_percent / 100))
    
    # Calculate position sizes (1/3 each)
    coin_per_entry = (total_money / buy_price) / 3
    positions = {
        "first": {"size": coin_per_entry, "active": True},
        "second": {"size": coin_per_entry, "active": False},
        "third": {"size": coin_per_entry, "active": False}
    }
    
    last_profit_target = buy_price
    current_target = initial_target
    
    print(f"📈 Entering first position: {coin_per_entry} {coin} at ${buy_price}")
    record_trade(coin, "buy", buy_price, f"Aggressive mode - First entry (1/3)")
    
    while True:
        current_price = getPrice(coin)
        
        # Check for target hits
        if current_price >= current_target:
            if not positions["second"]["active"]:
                # Enter second position
                positions["second"]["active"] = True
                print(f"📈 Entering second position at ${current_price}")
                record_trade(coin, "buy", current_price, f"Aggressive mode - Second entry (2/3)")
                current_target = second_target
                last_profit_target = current_price
            elif not positions["third"]["active"]:
                # Enter third position
                positions["third"]["active"] = True
                print(f"📈 Entering final position at ${current_price}")
                record_trade(coin, "buy", current_price, f"Aggressive mode - Final entry (3/3)")
                current_target = final_target
                last_profit_target = current_price
            else:
                # All positions entered, update trailing profit
                last_profit_target = current_target
                current_target *= (1 + (profit_percent / 100))
                print(f"📈 New profit target: ${current_target}")
        
        # Check for exit
        elif current_price < last_profit_target and any(p["active"] for p in positions.values()):
            total_position = sum(p["size"] for p in positions.values() if p["active"])
            avg_entry = buy_price  # Simplified average entry calculation
            profit = (current_price - avg_entry) * total_position
            print(f"✅ Taking profit on all active positions: ${profit:.2f}")
            record_trade(coin, "sell", current_price, f"Aggressive mode profit: ${profit:.2f}")
            return True
            
        time.sleep(10)

    print("✅ Trade closed. Restarting data collection...")