#!/usr/bin/env python3
"""
DEMO VERSION - Uses sample CSV data instead of live exchange data
This demonstrates the full functionality without requiring API access
"""

# Import the main system
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from btc_smart_money_system import (
    Config, DataFetcher, SignalGenerator,
    RiskManager, ChartVisualizer, Backtester
)

def main():
    """Demo application using sample data"""

    print("\n" + "="*60)
    print("INSTITUTIONAL BTC/USDT SMART MONEY SYSTEM - DEMO")
    print("="*60)
    print(f"Version: 1.0.0 (Demo Mode)")
    print(f"Strategy: ICT Smart Money + Fibonacci + Elliott Wave")
    print(f"Data Source: sample_btc_usdt_15m.csv")
    print("="*60 + "\n")

    # ========================================================================
    # STEP 1: Load Data from CSV
    # ========================================================================
    print("📁 Loading sample data from CSV...")

    df = DataFetcher.load_from_csv('sample_btc_usdt_15m.csv')

    if df.empty:
        print("✗ Failed to load sample data. Run generate_sample_data.py first.")
        return

    # Use same data for HTF (simplified for demo)
    htf_df = df.iloc[::4].copy()  # Every 4th candle = roughly 1-hour timeframe

    print(f"✓ Loaded {len(df)} candles")
    print(f"  Date range: {df.index[0]} to {df.index[-1]}")
    print(f"  Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")

    # ========================================================================
    # STEP 2: Signal Generation
    # ========================================================================
    generator = SignalGenerator(df, htf_df)
    signals = generator.generate_signals()

    if len(signals) == 0:
        print("\n⚠ No signals generated with current confluence settings.")
        print("   This is normal - the system is selective!")
        print("   Showing chart anyway for analysis...")

    # ========================================================================
    # STEP 3: Risk Management
    # ========================================================================
    if signals:
        print("\n💰 Calculating risk metrics...")
        signals = RiskManager.add_risk_metrics(signals, account_balance=10000)

        # Print top signals
        print("\n🏆 TOP TRADING SIGNALS:")
        print("="*60)
        for i, sig in enumerate(sorted(signals, key=lambda x: x['confidence'], reverse=True)[:10]):
            print(f"\n#{i+1} {sig['type']} Signal")
            print(f"  ├─ Entry: ${sig['entry_price']:.2f}")
            print(f"  ├─ Stop Loss: ${sig['stop_loss']:.2f}")
            print(f"  ├─ Take Profit: ${sig['take_profit']:.2f}")
            print(f"  ├─ Confidence: {sig['confidence']}/6 {'⭐' * sig['confidence']}")
            print(f"  ├─ R:R Ratio: 1:{sig['risk_reward']:.2f}")
            print(f"  ├─ Session: {sig.get('session', 'N/A')}")
            print(f"  └─ Factors: {', '.join(sig['factors'])}")

    # ========================================================================
    # STEP 4: Backtesting
    # ========================================================================
    if signals:
        backtester = Backtester(df, signals, initial_balance=10000)
        metrics = backtester.run_backtest()

        # Additional insights
        print("\n📊 PERFORMANCE INSIGHTS:")
        print("="*60)

        if metrics['win_rate'] >= 70:
            print("✅ Excellent win rate! System is performing well.")
        elif metrics['win_rate'] >= 60:
            print("✅ Good win rate. System is profitable.")
        elif metrics['win_rate'] >= 50:
            print("⚠️  Moderate win rate. Consider tighter confluence filters.")
        else:
            print("❌ Low win rate. Adjust parameters or wait for better market conditions.")

        if metrics['profit_factor'] >= 2.0:
            print("✅ Strong profit factor. Risk/reward is favorable.")
        elif metrics['profit_factor'] >= 1.5:
            print("✅ Good profit factor. System is profitable.")
        else:
            print("⚠️  Low profit factor. Consider adjusting targets.")

        if metrics['max_drawdown'] < 10:
            print("✅ Low drawdown. Risk management is effective.")
        elif metrics['max_drawdown'] < 20:
            print("⚠️  Moderate drawdown. Monitor position sizing.")
        else:
            print("❌ High drawdown. Reduce risk per trade or leverage.")

    # ========================================================================
    # STEP 5: Chart Visualization
    # ========================================================================
    print("\n📈 Creating interactive chart...")

    visualizer = ChartVisualizer(
        df=generator.df,
        signals=signals,
        order_blocks=generator.order_blocks,
        fvgs=generator.fvgs
    )

    fig = visualizer.create_chart()

    # Save chart
    output_file = 'btc_smart_money_chart_demo.html'
    fig.write_html(output_file)
    print(f"\n💾 Chart saved to: {output_file}")
    print("   📂 Open this file in your browser to view the interactive chart.")

    # ========================================================================
    # STEP 6: Export Signals
    # ========================================================================
    if signals:
        import pandas as pd
        signals_df = pd.DataFrame(signals)
        signals_csv = 'trading_signals_demo.csv'
        signals_df.to_csv(signals_csv, index=False)
        print(f"💾 Signals saved to: {signals_csv}")

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "="*60)
    print("✅ DEMO EXECUTION COMPLETE")
    print("="*60)
    print("\n📋 WHAT TO DO NEXT:")
    print("  1. Open btc_smart_money_chart_demo.html in your browser")
    print("  2. Study the detected Order Blocks (green/red zones)")
    print("  3. Examine Fair Value Gaps (blue/orange zones)")
    print("  4. Note the Golden Pocket zone (yellow highlight)")
    print("  5. Analyze signal placements and confluence factors")
    print("  6. Review trading_signals_demo.csv for detailed metrics")
    print("\n💡 TIP: This demo uses simulated data. For live trading:")
    print("     - Use btc_smart_money_system.py with exchange API")
    print("     - Start with paper trading to validate strategy")
    print("     - Reduce leverage to 10-50x for safety")
    print("     - Only risk 0.5-1% per trade")
    print("\n🎓 LEARNING RESOURCES:")
    print("     - Study Inner Circle Trader (ICT) on YouTube")
    print("     - Learn about liquidity sweeps and order blocks")
    print("     - Practice identifying these patterns manually first")
    print("\n⚠️  RISK WARNING: This is for educational purposes only!")
    print("    Cryptocurrency trading carries significant risk of loss.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
