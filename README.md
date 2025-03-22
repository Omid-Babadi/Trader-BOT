# 🤖 Bitcoin Trading Bot

A demo cryptocurrency trading bot with a modern UI that implements momentum-based trading strategies for Bitcoin. The bot features both default and aggressive trading modes, real-time price monitoring, and automated trade execution.

## 🌟 Features

- **Modern Cyberpunk-themed UI** built with tkinter and ttkbootstrap
- **Real-time Bitcoin price monitoring** using CoinGecko API
- **Two Trading Modes:**
  - **Default Mode:** Single entry with trailing profit targets
  - **Aggressive Mode:** Triple-entry strategy with scaled positions
- **Automated Trading Features:**
  - Momentum-based entry signals
  - Dynamic profit targets
  - Real-time trade history tracking
  - Risk management system
- **Live Market Analysis:**
  - 24-hour price change monitoring
  - 60-period moving average
  - Price trend analysis
  - Volume validation

## 📋 Requirements

- Python 3.8+
- Dependencies (installed via pip):
  ```
  pandas==2.2.3
  pycoingecko==3.2.0
  Requests==2.32.3
  numpy==1.26.4
  peewee==3.17.1
  ttkbootstrap==1.10.1
  ```

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Omid-Babadi/Trader-BOT.git
   cd traderBot
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```bash
   python ui.py
   ```

## 💡 How It Works

### Entry Conditions
- 24-hour price change >= 1%
- Current price above 60-period average
- Sufficient trading volume
- Less than 3 rejected signals per day

### Trading Modes

#### Default Mode
- Enters with full position size
- Example with $1000:
  ```
  Entry: Full $1000 at $50,000
  Target 1: $50,500 (+1%)
  Trailing stop: Moves up with each new high
  ```

#### Aggressive Mode
- Enters position in three parts
- Example with $1000:
  ```
  Entry 1: $333.33 at $50,000
  Entry 2: $333.33 at $50,500 (+1%)
  Entry 3: $333.33 at $51,005 (+1%)
  Final target: $51,515
  ```

## 🎮 Using the Bot

1. **Launch the Application:**
   - Run `python ui.py`
   - The modern Cyberpunk-themed UI will appear

2. **Configure Settings:**
   - Set your trading capital (default: $1000)
   - Choose trading mode (Default/Aggressive)
   - Adjust risk percentage and profit targets
   - Save your settings

3. **Start Trading:**
   - Click "Start Bot" to begin
   - Monitor live status in the Overview tab
   - Track trades in the History tab

4. **Monitor Performance:**
   - Real-time trade updates
   - Profit/Loss tracking
   - Trade history logging

## ⚠️ Disclaimer

This is a DEMO trading bot for educational purposes only. It should NOT be used for real trading without:
- Extensive testing
- Risk management implementation
- API key security measures
- Additional error handling
- Market condition safeguards

## 🔒 Security Notes

- Never store API keys in the code
- Use environment variables for sensitive data
- Implement proper error handling
- Add additional security measures before live trading

## 📊 Data Storage

The bot uses:
- SQLite database for price data
- JSON file for trade history
- Local storage for configuration

## 🛠 Technical Details

### Project Structure
```
traderBot/
├── database/
│   └── db.py
├── operation/
│   ├── getReady.py
│   └── strategy.py
├── main.py
├── market.py
├── trade_manager.py
├── ui.py
├── requirements.txt
└── README.md
```

### Key Components
- `ui.py`: Modern Cyberpunk-themed user interface
- `main.py`: Bot initialization and control
- `strategy.py`: Trading strategy implementation
- `trade_manager.py`: Trade execution and management
- `market.py`: Market data fetching via CoinGecko
- `db.py`: Database operations and trade history

## 🤝 Contributing

Feel free to:
- Fork the repository
- Create feature branches
- Submit pull requests
- Report issues
- Suggest improvements


## 🙏 Acknowledgments

- CoinGecko API for market data
- ttkbootstrap for UI theming
- Python community for libraries 