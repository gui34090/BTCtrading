#!/bin/bash
# BTC/USDT Smart Money Trading System - Quick Start Script

echo "================================================================================"
echo "BTC/USDT SMART MONEY TRADING SYSTEM - QUICK START"
echo "================================================================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Check required packages
echo ""
echo "📦 Checking required packages..."
python3 -c "
import sys
packages = ['pandas', 'numpy', 'plotly', 'ccxt', 'scipy', 'streamlit']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'   ✅ {pkg}')
    except ImportError:
        missing.append(pkg)
        print(f'   ❌ {pkg} - MISSING')

if missing:
    print(f'\n⚠️  Missing packages: {missing}')
    print(f'Install with: pip install {\" \".join(missing)}')
    sys.exit(1)
else:
    print('\n✅ All packages installed!')
"

if [ $? -ne 0 ]; then
    echo ""
    echo "Installing missing packages..."
    pip install pandas numpy plotly ccxt scipy streamlit
fi

echo ""
echo "================================================================================"
echo "CHOOSE HOW TO START:"
echo "================================================================================"
echo ""
echo "1. 📊 Live Dashboard (Recommended for beginners)"
echo "   - Interactive web interface"
echo "   - Real-time charts with signals"
echo "   - Multi-timeframe backtesting"
echo "   - Visual analysis tools"
echo ""
echo "2. 🔬 Run Backtest (Test strategy on historical data)"
echo "   - Test trading signals"
echo "   - See performance metrics"
echo "   - Validate strategy before live trading"
echo ""
echo "3. 🎯 Generate Signals (Get trading signals for current market)"
echo "   - Load latest data"
echo "   - Generate entry/exit signals"
echo "   - Get position sizing"
echo ""
echo "4. 📈 Fetch Live Data (Download latest BTC/USDT data)"
echo "   - Connect to Binance"
echo "   - Download 15m candles"
echo "   - Save to CSV for analysis"
echo ""
echo "================================================================================"
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting Live Dashboard..."
        echo "   Dashboard will open in your browser at http://localhost:8501"
        echo "   Press Ctrl+C to stop"
        echo ""
        streamlit run btc_live_dashboard.py
        ;;
    2)
        echo ""
        echo "🔬 Running Backtest..."
        python3 -c "
from btc_smart_money_system import DataFetcher, SignalGenerator, Backtester

# Load data
print('📊 Loading data...')
df = DataFetcher.load_from_csv('sample_btc_usdt_15m.csv')

# Generate signals
print('🎯 Generating signals...')
generator = SignalGenerator(df)
signals = generator.generate_signals()

# Run backtest
print('🔬 Running backtest...')
backtester = Backtester(df, signals, initial_balance=10000)
metrics = backtester.run_backtest()
"
        ;;
    3)
        echo ""
        echo "🎯 Generating Trading Signals..."
        python3 -c "
from btc_smart_money_system import DataFetcher, SignalGenerator, RiskManager

# Load data
print('📊 Loading data...')
df = DataFetcher.load_from_csv('sample_btc_usdt_15m.csv')

# Generate signals
print('🎯 Generating signals...')
generator = SignalGenerator(df)
signals = generator.generate_signals()

print(f'\n✅ Generated {len(signals)} trading signals\n')

for i, sig in enumerate(signals, 1):
    print(f'Signal #{i}:')
    print(f'  Type: {sig[\"type\"]}')
    print(f'  Entry: \${sig[\"entry_price\"]:,.2f}')
    print(f'  Stop Loss: \${sig[\"stop_loss\"]:,.2f}')
    print(f'  Take Profit: \${sig[\"take_profit\"]:,.2f}')
    print(f'  Confidence: {sig[\"confidence\"]}/12')
    print(f'  Risk:Reward: 1:{sig[\"risk_reward\"]:.2f}')
    print(f'  Factors: {\", \".join(sig[\"factors\"][:3])}...')
    print()
"
        ;;
    4)
        echo ""
        echo "📈 Fetching Live Data from Binance..."
        python3 -c "
from btc_smart_money_system import DataFetcher

fetcher = DataFetcher('binance')
df = fetcher.fetch_ohlcv('BTC/USDT', '15m', limit=500)

if len(df) > 0:
    filename = 'btc_usdt_15m_latest.csv'
    df.to_csv(filename)
    print(f'\n✅ Saved {len(df)} candles to {filename}')
else:
    print('\n❌ Failed to fetch data')
"
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run the script again and choose 1-4."
        exit 1
        ;;
esac

echo ""
echo "================================================================================"
echo "✅ Done!"
echo "================================================================================"
