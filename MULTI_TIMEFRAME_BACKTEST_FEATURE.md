# Multi-Timeframe Backtest Feature

## Overview
Added comprehensive multi-timeframe backtesting capability to the live dashboard, allowing users to compare strategy performance across different timeframes (5m, 15m, 1h, 4h).

## Features Added

### 1. Timeframe Selection
- ✅ 5 Minutes (5m)
- ✅ 15 Minutes (15m)
- ✅ 1 Hour (1h)
- ✅ 4 Hours (4h)

### 2. Configurable Parameters
- **Candles to Backtest:** 100-1000 (slider)
- **Multiple Timeframe Selection:** Test 1 or all timeframes simultaneously
- **Uses Current Settings:** Min confluence, account balance, risk per trade

### 3. Data Handling
**Demo Mode (CSV):**
- Loads sample data
- Resamples to 1H and 4H using OHLC aggregation
- Uses last N bars specified

**Live Mode (Binance):**
- Fetches real-time data for each timeframe
- Downloads actual candle data per timeframe
- No resampling needed

### 4. Results Display

#### Comparison Table
Displays for each timeframe:
- **Candles:** Total bars analyzed
- **Signals:** Total signals generated
- **Closed:** Completed trades
- **Open:** Trades still pending
- **Wins/Losses:** Trade outcomes
- **Win Rate:** Success percentage
- **Profit Factor:** Wins/Losses ratio
- **Net Profit:** Dollar profit/loss
- **ROI:** Return on investment %
- **Max DD:** Maximum drawdown %
- **Final Balance:** Ending account value

**Auto-highlights best performers** in green for:
- Highest Net Profit
- Highest ROI
- Highest Win Rate

#### Performance Visualization

**Chart 1: ROI by Timeframe**
- Bar chart showing ROI for each timeframe
- Green bars = profit, Red bars = loss
- Values displayed on bars

**Chart 2: Signals & Win Rate**
- Blue bars = Total signals generated
- Gold line = Win rate percentage
- Dual Y-axis for easy comparison

### 5. Smart Recommendations

Automatically identifies and highlights:
- **Best ROI:** Timeframe with highest returns
- **Most Signals:** Timeframe generating most opportunities
- **Best Win Rate:** Most consistent performer

Provides actionable recommendation based on results.

## Usage

### From Dashboard:
1. Launch dashboard: `streamlit run btc_live_dashboard.py`
2. Scroll to "🔬 Multi-Timeframe Backtest" expander
3. Select timeframes to test (checkboxes)
4. Adjust number of candles (100-1000)
5. Click "🚀 Run Multi-Timeframe Backtest"
6. View results and charts

### Example Output:
```
📊 Backtest Results Comparison

Timeframe  | Candles | Signals | Closed | Wins | Win Rate | ROI    | Net Profit
-----------|---------|---------|--------|------|----------|--------|------------
5 Minutes  | 500     | 8       | 3      | 2    | 66.7%    | 2.50%  | $250.00
15 Minutes | 500     | 3       | 1      | 1    | 100.0%   | 1.00%  | $100.00 ✓
1 Hour     | 125     | 1       | 0      | 0    | 0.0%     | 0.00%  | $0.00
4 Hours    | 31      | 0       | 0      | 0    | 0.0%     | 0.00%  | $0.00

💡 Recommendations:
- Best ROI: 5 Minutes (2.50%)
- Most Signals: 5 Minutes (8 trades)
- Best Win Rate: 15 Minutes (100.0%)

💡 Consider using 5 Minutes for optimal risk-adjusted returns.
```

## Technical Implementation

### Key Functions

**Timeframe Resampling (Demo Mode):**
```python
if tf == "1h":
    test_df = test_df.resample('1H', on=test_df.index).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
```

**Live Data Fetching:**
```python
fetcher = DataFetcher('binance')
test_df = fetcher.fetch_ohlcv(Config.SYMBOL, tf, limit=backtest_bars)
```

**Backtest Execution:**
```python
test_generator = SignalGenerator(test_df)
test_signals = test_generator.generate_signals()
backtester = Backtester(test_df, test_signals, initial_balance=account_balance)
metrics = backtester.run_backtest()
```

### Progress Tracking
- Real-time progress bar
- Status updates per timeframe
- Graceful error handling

## Benefits

### 1. Strategy Optimization
- Identify best timeframe for your strategy
- Compare risk/reward across timeframes
- Optimize for win rate vs profit

### 2. Risk Management
- Understand drawdown per timeframe
- See signal frequency differences
- Choose appropriate timeframe for risk appetite

### 3. Time Efficiency
- Test multiple timeframes in one click
- Visual comparison for quick decisions
- No manual switching needed

### 4. Data-Driven Decisions
- Objective performance metrics
- Clear visual comparisons
- Automated recommendations

## Performance Insights

### Typical Patterns:

**Lower Timeframes (5m, 15m):**
- ✅ More signals
- ✅ More trading opportunities
- ⚠️ More noise, lower win rate
- ⚠️ Requires tighter stops

**Higher Timeframes (1h, 4h):**
- ✅ Higher win rate
- ✅ Better trend following
- ⚠️ Fewer signals
- ⚠️ Requires more capital

### Recommendation Matrix:

| Goal                    | Best Timeframe | Reason                          |
|-------------------------|----------------|---------------------------------|
| Maximum Profit          | 5m or 15m      | More opportunities              |
| Highest Win Rate        | 1h or 4h       | Cleaner trends                  |
| Balanced Approach       | 15m            | Good signals + decent win rate  |
| Low Maintenance         | 4h             | Fewer trades to manage          |
| Day Trading             | 5m or 15m      | Quick entries/exits             |
| Swing Trading           | 1h or 4h       | Hold positions longer           |

## Files Modified

### btc_live_dashboard.py
- **Line 19:** Added `Backtester` import
- **Lines 483-749:** New multi-timeframe backtest section
  - Timeframe selection UI
  - Data fetching/resampling logic
  - Backtest execution loop
  - Results comparison table
  - Performance visualization charts
  - Smart recommendations

## Future Enhancements

Potential additions:
1. **More Timeframes:** Add 30m, 2h, daily, weekly
2. **Historical Period Selection:** Choose specific date ranges
3. **Walk-Forward Testing:** Sliding window backtests
4. **Monte Carlo Simulation:** Statistical robustness testing
5. **Export Results:** Download backtest data as CSV
6. **Risk Metrics:** Sharpe ratio, Sortino ratio, Calmar ratio
7. **Equity Curve:** Visual P&L over time per timeframe
8. **Trade-by-Trade Analysis:** Detailed trade logs

## Testing

Run dashboard:
```bash
streamlit run btc_live_dashboard.py
```

Navigate to "🔬 Multi-Timeframe Backtest" section and test with:
1. Demo mode (CSV data)
2. Different timeframe combinations
3. Various confluence scores
4. Different candle counts

## Conclusion

The multi-timeframe backtest feature provides traders with powerful tools to:
- Compare strategy performance objectively
- Make data-driven timeframe selections
- Optimize trading parameters
- Understand risk/reward tradeoffs

All integrated seamlessly into the live dashboard with beautiful visualizations and actionable insights.
