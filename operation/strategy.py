from market import getPrice, changesof24h
from database.db import record_trade, load_trade_history, Market, clear_database
import datetime

BUY_SIGNAL = "buy"
NOT_BUY_SIGNAL = "keep"
REJECT_SIGNAL = "reject"

class TradingStrategy:
    def __init__(self, total_money=1000, risk_percentage=2, mode="default", target_profit=1):
        self.total_money = float(total_money)
        self.risk_percentage = float(risk_percentage)
        self.mode = mode.lower()
        self.target_profit = float(target_profit)
        clear_database()  # Clear ranges on startup
        
    def momentum_based_entry_signal(self, coin, level_of_entry):
        """
        Determines if a buy signal should be generated based on price momentum.
        """
        print(f"📊 momentum_based_entry_signal: Checking {coin}, entry level: {level_of_entry}")
        history = changesof24h(coin)
        print(f"📈 24h change for {coin}: {history}%")

        if float(history) >= 1:
            print(f"✅ Positive momentum detected for {coin}")
            return self.safe_filter_buying(coin, level_of_entry + 1)
        else:
            print(f"⏸️ Insufficient momentum for {coin}")
            return NOT_BUY_SIGNAL, 0

    def safe_filter_buying(self, market_name, level_of_entry):
        """
        Checks average price of last 60 trades before allowing a buy.
        """
        print(f"🛡️ safe_filter_buying: Checking {market_name}, entry level: {level_of_entry}")

        try:
            market = Market.get(Market.name == market_name)
            price_ranges = market.get_price_ranges()
            print(f"📊 Found {len(price_ranges)} price points for {market_name}")

            if len(price_ranges) < 60:
                print(f"⚠️ Not enough data for {market_name}.")
                return REJECT_SIGNAL, 0

            avg_price = sum(price_ranges) / len(price_ranges)
            current_price = getPrice(market_name)
            print(f"💲 {market_name} - Avg price: {avg_price}, Current price: {current_price}")

            if avg_price < current_price:
                print(f"✅ Price trending upward for {market_name}")
                return self.history_check(market_name, level_of_entry + 1)
            else:
                print(f"❌ Price not trending upward for {market_name}")
                return REJECT_SIGNAL, 0

        except Market.DoesNotExist:
            print(f"❌ Market {market_name} does not exist in database")
            return REJECT_SIGNAL, 0

    def history_check(self, coin, level_of_entry):
        """
        Checks if there were 3 rejected buy signals today. If so, stops trading.
        """
        print(f"🔍 history_check: Checking {coin}, entry level: {level_of_entry}")
        trade_data = load_trade_history()
        today = datetime.datetime.now().date()
        print(f"📅 Analyzing trading history for {coin} on {today}")

        bad_signals_today = sum(
            1 for trade in trade_data
            if trade["coin"] == coin and trade.get("signal") == "reject" and 
            datetime.datetime.fromisoformat(trade["timestamp"]).date() == today
        )
        print(f"❗ Found {bad_signals_today} rejected signals today for {coin}")

        if bad_signals_today >= 3:
            print(f"🚫 Too many bad signals for {coin} today.")
            return REJECT_SIGNAL, 0

        current_price = getPrice(coin)
        print(f"💰 Recording BUY trade for {coin} at price {current_price}")
        record_trade(coin, "buy", current_price, f"Entry with {self.mode} mode")
        print(f"✅ BUY signal generated for {coin} at level {level_of_entry}")
        return BUY_SIGNAL, level_of_entry
