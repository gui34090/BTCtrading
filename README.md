# 🏦 Institutional-Grade BTC/USDT Smart Money Trading System

> A sophisticated algorithmic trading system implementing Smart Money Concepts (ICT), Fibonacci analysis, and Elliott Wave theory for high-probability BTC/USDT intraday trading.

![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Core Strategy](#core-strategy)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [System Components](#system-components)
- [Trading Signals](#trading-signals)
- [Risk Management](#risk-management)
- [Backtesting](#backtesting)
- [Configuration](#configuration)
- [Visualization](#visualization)
- [Disclaimer](#disclaimer)

---

## 🎯 Overview

This institutional-grade trading system is designed for sophisticated crypto traders who understand **Smart Money Concepts** and **Inner Circle Trader (ICT)** methodology. The system automatically identifies high-probability trading opportunities by analyzing:

- **Liquidity Pools** and institutional stop hunts
- **Order Blocks** (institutional footprints)
- **Fair Value Gaps** (FVGs) - price inefficiencies
- **Break of Structure** (BOS) and **Change of Character** (ChoCh)
- **Fibonacci Golden Pocket** (61.8%-78.6% retracements)
- **Session-based** timing (London/NY opens)
- **Multi-timeframe** confluence analysis

### Key Philosophy

The system trades **with** institutional money flow, not against it. By identifying engineered liquidity events and structural changes, it positions trades where "smart money" is likely to enter, achieving:

- ✅ High win rates (60-80%+ with proper confluence)
- ✅ Favorable risk/reward ratios (2:1 to 5:1)
- ✅ Precise entry timing during high-liquidity sessions
- ✅ Algorithmic consistency without emotional bias

---

## 🧠 Core Strategy

### 1. Primary Trading Strategies

#### 1.1 Liquidity Sweep & Reversal
- Identifies stop hunts beyond swing highs/lows
- Waits for rejection and reversal confirmation
- Enters on the institutional move back into range

#### 1.2 Liquidity Grab into FVG
- Combines liquidity sweep with Fair Value Gap
- Targets gap fills as high-probability zones
- Uses FVG as precise entry and target area

#### 1.3 Engineered Liquidity & False Breakouts
- Detects failed breakouts designed to trap retail traders
- Identifies reversal candles (long wicks)
- Enters opposite direction of false breakout

#### 1.4 Run on Stops
- Monitors rapid moves through multiple stop layers
- Identifies exhaustion and volume climax
- Enters on snap-back reversal

### 2. The Confluence Stack

A signal is only generated when **at least 3** of these factors align:

1. **Market Structure Context** (BOS/ChoCh on HTF)
2. **Liquidity Sweep** (stop hunt confirmation)
3. **Order Block** (institutional footprint)
4. **Fair Value Gap** (price inefficiency)
5. **Golden Pocket** (61.8%-78.6% Fibonacci)
6. **Session Timing** (London/NY open)

### 3. Fibonacci Integration

- **Discount Zone** (0%-50%): Optimal long entries
- **Premium Zone** (50%-100%): Optimal short entries
- **Golden Pocket** (61.8%-78.6%): Highest-probability entry zone
- **Extensions** (127.2%, 161.8%, 261.8%): Profit targets

---

## ✨ Features

### Smart Money Detection
- ✅ Automated swing high/low identification
- ✅ Order Block detection (bullish & bearish)
- ✅ Fair Value Gap scanning with mitigation tracking
- ✅ Break of Structure and Change of Character analysis
- ✅ Liquidity sweep identification (stop hunts)

### Fibonacci Analysis
- ✅ Premium/Discount array mapping
- ✅ Golden Pocket highlighting (61.8%-78.6%)
- ✅ Multi-level retracements (11.4%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 88.6%)
- ✅ Extension projections for profit targets (161.8%, 261.8%)

### Session-Based Filtering
- ✅ London session (08:00-10:00 UTC) detection
- ✅ New York session (13:30-15:30 UTC) detection
- ✅ Automatic session-based signal filtering

### Risk Management
- ✅ Dynamic position sizing based on risk per trade
- ✅ Automatic stop-loss calculation below/above swing points
- ✅ Fibonacci-based take-profit targets
- ✅ Risk/reward ratio calculation per signal
- ✅ High-leverage optimization (200x default)

### Backtesting Engine
- ✅ Historical performance simulation
- ✅ Win rate and profit factor calculation
- ✅ Maximum drawdown tracking
- ✅ ROI and net profit metrics
- ✅ Trade-by-trade outcome analysis

### Visualization
- ✅ Interactive Plotly charts (dark theme)
- ✅ Candlestick + volume visualization
- ✅ Order Block and FVG zone overlays
- ✅ Fibonacci level plotting with Golden Pocket highlight
- ✅ Signal markers with confidence scoring
- ✅ Session timing annotations
- ✅ Hover tooltips with detailed information

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Internet connection (for live data fetching)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd BTCtrading
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `scipy` - Scientific computing
- `plotly` - Interactive charting
- `ccxt` - Exchange connectivity

### Step 3: Verify Installation

```bash
python btc_smart_money_system.py
```

---

## 📖 Usage

### Basic Usage (Live Data from Binance)

```bash
python btc_smart_money_system.py
```

This will:
1. Fetch latest 500 candles of BTC/USDT (15-minute timeframe)
2. Analyze Smart Money patterns
3. Generate trading signals
4. Run backtest simulation
5. Create interactive HTML chart (`btc_smart_money_chart.html`)
6. Export signals to CSV (`trading_signals.csv`)

### Using Historical CSV Data

Edit `btc_smart_money_system.py` line ~1475:

```python
# Replace live fetching with CSV loading
df = DataFetcher.load_from_csv('your_data.csv')
```

**CSV Format Requirements:**
- Columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`
- Timestamp: ISO 8601 format or Unix milliseconds
- Example: `2025-01-13 12:00:00,95000.5,95500.0,94800.0,95200.0,1234.56`

### Viewing Results

1. **Interactive Chart**: Open `btc_smart_money_chart.html` in your browser
2. **Signal Data**: Open `trading_signals.csv` in Excel/spreadsheet
3. **Console Output**: View backtest metrics in terminal

---

## 🔧 System Components

### 1. `DataFetcher`
- Connects to Binance via CCXT
- Fetches OHLCV data for any timeframe
- Supports CSV file loading for backtesting

### 2. `SmartMoneyDetector`
- **`detect_swing_points()`**: Identifies swing highs/lows
- **`detect_order_blocks()`**: Finds institutional footprints
- **`detect_fvg()`**: Locates Fair Value Gaps
- **`detect_market_structure()`**: Tracks BOS/ChoCh
- **`detect_liquidity_sweep()`**: Identifies stop hunts

### 3. `FibonacciAnalyzer`
- **`calculate_retracements()`**: Premium/Discount arrays
- **`calculate_extensions()`**: Profit target projections
- **`is_in_golden_pocket()`**: Optimal entry zone detection
- **`is_in_discount_zone()`**: Long entry area check
- **`is_in_premium_zone()`**: Short entry area check

### 4. `SessionFilter`
- **`get_session()`**: Determines London/NY session
- **`is_high_liquidity_session()`**: Validates trading time
- **`add_session_column()`**: Enriches data with session info

### 5. `SignalGenerator`
- **`_calculate_confluence_score()`**: Evaluates signal quality
- **`generate_signals()`**: Creates buy/sell signals
- Integrates all detection methods
- Applies multi-factor confluence logic

### 6. `RiskManager`
- **`calculate_position_size()`**: Risk-based sizing
- **`calculate_risk_reward()`**: R:R ratio per trade
- **`add_risk_metrics()`**: Enriches signals with risk data

### 7. `ChartVisualizer`
- **`create_chart()`**: Builds interactive Plotly figure
- Overlays all technical elements
- Color-coded signals by confidence
- Exports to HTML for browser viewing

### 8. `Backtester`
- **`run_backtest()`**: Simulates historical performance
- Tracks wins, losses, drawdown
- Calculates profit factor and ROI
- Prints comprehensive metrics report

---

## 📊 Trading Signals

### Signal Structure

Each signal contains:

```python
{
    'timestamp': datetime,        # Signal generation time
    'type': 'LONG' or 'SHORT',   # Direction
    'entry_price': float,         # Entry price
    'stop_loss': float,           # Stop loss level
    'take_profit': float,         # Take profit target (161.8% Fib)
    'confidence': int,            # Confluence score (3-6)
    'factors': list,              # List of confluence factors
    'session': str,               # 'London' or 'New York'
    'risk_reward': float,         # R:R ratio
    'position_size': float,       # BTC amount to trade
    'leveraged_size': float,      # With leverage applied
    'risk_amount': float          # Dollar risk per trade
}
```

### Confidence Scoring

- **Score 3**: Minimum viable signal (3 confluences)
- **Score 4**: Good signal (4 confluences)
- **Score 5**: Strong signal (5 confluences)
- **Score 6**: Perfect signal (all confluences aligned) ⭐

### Example Signal Output

```
🟢 LONG @ 95234.50 | Confidence: 5 | Liquidity Sweep, Order Block, FVG, Golden Pocket, London Session
   SL: $94,850.00 | TP: $97,500.00
   R:R = 1:5.89
   Position Size: 0.026 BTC (Leveraged: 5.2 BTC @ 200x)
```

---

## ⚖️ Risk Management

### Position Sizing Formula

```
Risk Amount = Account Balance × Risk Per Trade (1%)
Position Size = Risk Amount ÷ Distance to Stop Loss
Leveraged Size = Position Size × Leverage (200x)
```

### Default Settings

- **Risk Per Trade**: 1% of account balance
- **Leverage**: 200x (adjustable for lower risk)
- **Stop Loss Placement**:
  - Longs: 0.2% below swing low
  - Shorts: 0.2% above swing high
- **Take Profit**: 161.8% Fibonacci extension

### Recommended Guidelines

1. **Never risk more than 1-2% per trade**
2. **Only take signals with confidence ≥ 4** (for beginners)
3. **Trade only during London/NY sessions**
4. **Wait for HTF alignment** (higher timeframe bias)
5. **Use proper leverage** (10-50x for most traders, 200x for experts only)

---

## 📈 Backtesting

### Metrics Explained

- **Win Rate**: Percentage of profitable trades
  - Target: 60-80% (with confluence filtering)

- **Profit Factor**: Gross profit ÷ Gross loss
  - Target: > 2.0 (system default targets 2-5)

- **Max Drawdown**: Largest peak-to-trough decline
  - Target: < 20% (with 1% risk per trade)

- **ROI**: Return on Investment percentage
  - Varies by market conditions

### Sample Backtest Output

```
============================================================
BACKTEST RESULTS
============================================================
Total Trades:     47
Wins:             32 (68.1%)
Losses:           15
Profit Factor:    3.24
Net Profit:       $12,450.00
ROI:              124.50%
Max Drawdown:     8.35%
Final Balance:    $22,450.00
============================================================
```

---

## ⚙️ Configuration

### Editing `Config` Class

Open `btc_smart_money_system.py` and modify the `Config` class (lines ~33-81):

```python
class Config:
    # Data settings
    SYMBOL = "BTC/USDT"          # Trading pair
    TIMEFRAME = "15m"            # Signal timeframe (5m, 15m, 1h)
    HTF_TIMEFRAME = "4h"         # Higher timeframe bias (1h, 4h, 1d)
    LOOKBACK_BARS = 500          # Historical data to analyze

    # Smart Money
    SWING_LENGTH = 10            # Swing detection sensitivity
    OB_THRESHOLD = 0.002         # Order Block minimum move (0.2%)
    FVG_THRESHOLD = 0.001        # FVG minimum gap (0.1%)

    # Sessions (UTC)
    LONDON_SESSION = (8, 10)     # London open hours
    NY_SESSION = (13, 15)        # NY open hours

    # Signal filtering
    MIN_CONFLUENCE_SCORE = 3     # Minimum factors required

    # Risk management
    RISK_PER_TRADE = 0.01        # 1% risk per trade
    LEVERAGE = 200               # Leverage multiplier
```

### Timeframe Recommendations

- **5-minute**: Scalping (very active, more signals)
- **15-minute**: Intraday swing trading (balanced)
- **1-hour**: Position trading (fewer, higher-quality signals)

### Customizing Fibonacci Levels

Edit `FIB_RETRACEMENT_LEVELS` and `FIB_EXTENSION_LEVELS` dictionaries to add/remove levels.

---

## 📺 Visualization

### Chart Features

The generated HTML chart includes:

1. **Candlestick Chart**
   - Green = bullish candles
   - Red = bearish candles

2. **Volume Bars**
   - Color-matched to candle direction
   - Identifies high-volume confirmation

3. **Swing Points**
   - 🔶 Orange triangles = Swing highs
   - 🔷 Blue triangles = Swing lows

4. **Order Blocks**
   - Green zones = Bullish OBs
   - Red zones = Bearish OBs

5. **Fair Value Gaps**
   - Blue dotted zones = Bullish FVGs
   - Orange dotted zones = Bearish FVGs

6. **Fibonacci Levels**
   - Horizontal dashed lines
   - 🟡 Golden Pocket = Yellow shaded area (61.8%-78.6%)

7. **Trading Signals**
   - 🟢 Green triangle up = LONG signal
   - 🔴 Red triangle down = SHORT signal
   - Size = Confidence level

8. **Session Markers**
   - Annotations for London/NY opens

### Interactive Features

- **Zoom**: Scroll or drag to zoom
- **Pan**: Click and drag to move chart
- **Hover**: See detailed info on any element
- **Legend**: Click to show/hide layers
- **Export**: Save as PNG via chart toolbar

---

## ⚠️ Disclaimer

### Important Risk Warnings

1. **High Risk**: Cryptocurrency trading, especially with leverage, carries substantial risk of loss. You may lose your entire investment.

2. **Not Financial Advice**: This software is for educational and research purposes only. It does not constitute financial, investment, or trading advice.

3. **No Guarantees**: Past performance does not guarantee future results. Backtested results may not reflect actual trading conditions.

4. **Leverage Danger**: The default 200x leverage is **EXTREMELY RISKY** and suitable only for professional traders. Most traders should use 10-50x maximum.

5. **Do Your Research**: Understand Smart Money Concepts, Fibonacci analysis, and risk management before trading real capital.

6. **Start Small**: Always test with paper trading or small positions first.

7. **Exchange Risks**: Cryptocurrency exchanges can experience downtime, hacks, or insolvency.

### Recommended Practice

1. Paper trade for at least 1-3 months
2. Start with 0.1% risk per trade
3. Use maximum 10x leverage initially
4. Never trade money you can't afford to lose
5. Continuously educate yourself on ICT methodology

---

## 📚 Additional Resources

### Smart Money Concepts (ICT)

- Inner Circle Trader YouTube channel
- ICT Mentorship 2022 (free course)
- Smart Money Concepts Discord communities

### Fibonacci & Elliott Wave

- "Elliott Wave Principle" by Frost & Prechter
- Fibonacci studies by Leonardo Fibonacci
- Harmonic trading patterns

### Risk Management

- "Trading in the Zone" by Mark Douglas
- "The New Trading for a Living" by Dr. Alexander Elder
- Position sizing calculators

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear comments
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

---

## 💬 Support

For questions, issues, or discussions:

- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions tab
- **Email**: [Your contact email]

---

## 🌟 Acknowledgments

- Inner Circle Trader (Michael Huddleston) for Smart Money Concepts
- The ICT community for sharing knowledge
- CCXT library for exchange connectivity
- Plotly team for excellent visualization tools

---

**Happy Trading! Remember: Trade smart, trade safe, and always manage your risk.** 🚀📈

---

*Last Updated: 2025-01-13*
*Version: 1.0.0*
