import time
import datetime
from database.db import initialize_database, close_database, Market, clear_database
from operation.getReady import makeReady
from operation.strategy import TradingStrategy
from trade_manager import manage_trade
from market import getPrice, changesof24h

class TradingBot:
    def __init__(self, total_money=1000, risk_percentage=2, mode="default", target_profit=1):
        self.strategy = TradingStrategy(
            total_money=total_money,
            risk_percentage=risk_percentage,
            mode=mode,
            target_profit=target_profit
        )
        self.total_money = float(total_money)
        self.mode = mode.lower()
        self.target_profit = float(target_profit)
        self.is_running = False
        
    def start(self, coin="bitcoin"):
        """Start the trading bot"""
        self.is_running = True
        print(f"[{datetime.datetime.now()}] === Trading Bot Started ===")
        print(f"[{datetime.datetime.now()}] Mode: {self.mode}, Money: ${self.total_money}")
        self.marketValidation(coin)
        
    def stop(self):
        """Stop the trading bot"""
        self.is_running = False
        print(f"[{datetime.datetime.now()}] === Trading Bot Stopped ===")
        
    def marketValidation(self, coin):
        """
        Collects price data every minute until 60 data points are available.
        Then, it starts trade execution.
        """
        print(f"[{datetime.datetime.now()}] Starting market validation for {coin}")
        while self.is_running:
            try:
                initialize_database()
                price, changes24 = makeReady(coin)
                print(f"[{datetime.datetime.now()}] Current {coin} price: ${price:.2f}, 24h change: {changes24:.2f}%")

                market, created = Market.get_or_create(name=coin)
                if created:
                    print(f"[{datetime.datetime.now()}] Created new market entry for {coin}")
                
                price_ranges = market.get_price_ranges()
                changes_range = market.get_changes_range()

                price_ranges.append(price)
                changes_range.append(changes24)

                # Keep last 60 values
                price_ranges = price_ranges[-60:]
                changes_range = changes_range[-60:]

                market.set_price_ranges(price_ranges)
                market.set_changes_range(changes_range)
                market.save()

                print(f"[{datetime.datetime.now()}] Collected price point {len(price_ranges)}/60 for {coin}: ${price:.2f}")

                if len(price_ranges) == 60:
                    print(f"[{datetime.datetime.now()}] ✅ 60 prices collected for {coin}. Ready to check trade signals.")
                    self.performAction(price_ranges, changes_range, coin)
                    break  # Stop collecting once trade starts

            except Exception as e:
                print(f"[{datetime.datetime.now()}] ERROR in market validation: {str(e)}")
            finally:
                close_database()

            if not self.is_running:
                break
                
            time.sleep(10)

    def wait_for_new_data(self, coin):
        """
        Waits for 60 new price updates before re-checking buy signals.
        """
        print(f"[{datetime.datetime.now()}] Starting new data collection cycle for {coin}")
        while self.is_running:
            try:
                initialize_database()
                market = Market.get(Market.name == coin)
                starting_price_data = len(market.get_price_ranges())
                print(f"[{datetime.datetime.now()}] Starting with {starting_price_data} existing price points")

                while len(market.get_price_ranges()) < starting_price_data + 60 and self.is_running:
                    price, changes24 = makeReady(coin)
                    
                    price_ranges = market.get_price_ranges()
                    changes_range = market.get_changes_range()

                    price_ranges.append(price)
                    changes_range.append(changes24)

                    price_ranges = price_ranges[-60:]
                    changes_range = changes_range[-60:]

                    market.set_price_ranges(price_ranges)
                    market.set_changes_range(changes_range)
                    market.save()

                    current_count = len(price_ranges) - starting_price_data
                    print(f"[{datetime.datetime.now()}] Waiting for new price data... {current_count}/60 collected (${price:.2f}, {changes24:.2f}%)")
                    time.sleep(60)

                if self.is_running:
                    print(f"[{datetime.datetime.now()}] ✅ 60 new prices collected for {coin}. Resuming trading...")
                    break

            except Exception as e:
                print(f"[{datetime.datetime.now()}] ERROR during price data collection: {str(e)}")

            finally:
                close_database()

    def performAction(self, price_ranges, changes_range, coin):
        """
        Checks buy/sell signals and executes trades accordingly.
        After a trade is closed, it waits for another 60 new prices before attempting to trade again.
        """
        print(f"[{datetime.datetime.now()}] Entering trading mode for {coin}")
        while self.is_running:
            signal, level = self.strategy.momentum_based_entry_signal(coin, 1)
            print(f"[{datetime.datetime.now()}] Strategy signal for {coin}: {signal} (strength level: {level})")

            if signal == "buy":
                buy_price = getPrice(coin)
                print(f"[{datetime.datetime.now()}] 💰 BUY SIGNAL detected at ${buy_price:.2f}. Opening trade...")
                
                trade_closed = manage_trade(
                    coin=coin,
                    buy_price=buy_price,
                    total_money=self.total_money,
                    mode=self.mode,
                    profit_percent=self.target_profit
                )
                
                if trade_closed and self.is_running:
                    print(f"[{datetime.datetime.now()}] 🔄 Trade closed. Waiting for 60 new price updates before next buy attempt...")
                    self.wait_for_new_data(coin)
            else:
                print(f"[{datetime.datetime.now()}] 🚫 No buy signal for {coin}. Waiting...")

            if not self.is_running:
                break
                
            time.sleep(60)

# This will be called from the UI
def start_bot(total_money=1000, risk_percentage=2, mode="default", target_profit=1):
    bot = TradingBot(
        total_money=total_money,
        risk_percentage=risk_percentage,
        mode=mode,
        target_profit=target_profit
    )
    return bot
