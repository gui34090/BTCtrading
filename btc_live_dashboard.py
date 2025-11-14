#!/usr/bin/env python3
"""
Live BTC/USDT Smart Money Dashboard
Interactive web application with auto-refreshing charts
Run with: streamlit run btc_live_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# Import our trading system
from btc_smart_money_system import (
    Config, DataFetcher, SignalGenerator,
    RiskManager, SmartMoneyDetector, FibonacciAnalyzer
)

# Page configuration
st.set_page_config(
    page_title="BTC/USDT Smart Money Live Chart",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main { background-color: #0E1117; }
    .stMetric { background-color: #262730; padding: 10px; border-radius: 5px; }
    h1 { color: #26a69a; }
    h2, h3 { color: #ffd700; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🏦 Institutional BTC/USDT Smart Money Dashboard")
st.markdown("**Live Analysis** • Smart Money Concepts • Golden Pocket • Liquidity Analysis")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Settings")

    data_source = st.radio(
        "Data Source",
        ["Live (Binance)", "Demo (CSV)"],
        index=1  # Default to demo for safety
    )

    timeframe = st.selectbox(
        "Timeframe",
        ["5m", "15m", "1h", "4h"],
        index=1  # 15m default
    )

    lookback_bars = st.slider(
        "Bars to Analyze",
        min_value=100,
        max_value=1000,
        value=500,
        step=50
    )

    min_confluence = st.slider(
        "Min Confluence Score",
        min_value=2,
        max_value=5,
        value=3,
        help="Minimum factors required for signal"
    )

    auto_refresh = st.checkbox("Auto Refresh", value=False)
    refresh_interval = st.number_input(
        "Refresh Interval (seconds)",
        min_value=30,
        max_value=300,
        value=60,
        step=30
    )

    st.markdown("---")
    st.markdown("### 📊 Risk Settings")

    account_balance = st.number_input(
        "Account Balance ($)",
        min_value=100,
        max_value=1000000,
        value=10000,
        step=1000
    )

    risk_per_trade = st.slider(
        "Risk Per Trade (%)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1
    )

    leverage = st.selectbox(
        "Leverage",
        [10, 25, 50, 75, 100, 125, 200],
        index=4  # 100x default
    )

    if st.button("🔄 Refresh Now"):
        st.rerun()

# Cache data fetching
@st.cache_data(ttl=60)
def fetch_market_data(source, timeframe, bars):
    """Fetch market data with caching"""
    if source == "Demo (CSV)":
        try:
            df = DataFetcher.load_from_csv('sample_btc_usdt_15m.csv')
            # Take last N bars
            df = df.iloc[-bars:]
            htf_df = df.iloc[::4].copy()
            return df, htf_df, "success"
        except Exception as e:
            return None, None, f"Error loading CSV: {e}"
    else:
        # Live data from Binance
        try:
            fetcher = DataFetcher('binance')
            df = fetcher.fetch_ohlcv(Config.SYMBOL, timeframe, limit=bars)
            htf_timeframe = "4h" if timeframe in ["5m", "15m"] else "1d"
            htf_df = fetcher.fetch_ohlcv(Config.SYMBOL, htf_timeframe, limit=100)

            if df.empty:
                return None, None, "Failed to fetch data from exchange"

            return df, htf_df, "success"
        except Exception as e:
            return None, None, f"Exchange error: {e}"

def create_live_chart(df, signals, order_blocks, fvgs):
    """Create Plotly chart optimized for Streamlit"""

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=('Price Action', 'Volume')
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='BTC/USDT',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )

    # Volume
    colors = ['#26a69a' if c >= o else '#ef5350'
              for c, o in zip(df['close'], df['open'])]
    fig.add_trace(
        go.Bar(x=df.index, y=df['volume'], marker_color=colors,
               opacity=0.5, name='Volume', showlegend=False),
        row=2, col=1
    )

    # Swing points
    if 'swing_high' in df.columns:
        swing_highs = df[df['swing_high']]
        if len(swing_highs) > 0:
            fig.add_trace(
                go.Scatter(
                    x=swing_highs.index, y=swing_highs['high'],
                    mode='markers', name='Swing High',
                    marker=dict(symbol='triangle-down', size=8, color='#ff9800')
                ),
                row=1, col=1
            )

    if 'swing_low' in df.columns:
        swing_lows = df[df['swing_low']]
        if len(swing_lows) > 0:
            fig.add_trace(
                go.Scatter(
                    x=swing_lows.index, y=swing_lows['low'],
                    mode='markers', name='Swing Low',
                    marker=dict(symbol='triangle-up', size=8, color='#2196f3')
                ),
                row=1, col=1
            )

    # Order Blocks
    for ob in order_blocks.get('bullish', [])[-10:]:
        fig.add_shape(
            type="rect", x0=ob['timestamp'], x1=df.index[-1],
            y0=ob['low'], y1=ob['high'],
            fillcolor="rgba(38, 166, 154, 0.15)",
            line=dict(color="rgba(38, 166, 154, 0.5)", width=1),
            layer='below', row=1, col=1
        )

    for ob in order_blocks.get('bearish', [])[-10:]:
        fig.add_shape(
            type="rect", x0=ob['timestamp'], x1=df.index[-1],
            y0=ob['low'], y1=ob['high'],
            fillcolor="rgba(239, 83, 80, 0.15)",
            line=dict(color="rgba(239, 83, 80, 0.5)", width=1),
            layer='below', row=1, col=1
        )

    # FVGs
    for fvg in fvgs.get('bullish', [])[-5:]:
        fig.add_shape(
            type="rect", x0=fvg['timestamp'], x1=df.index[-1],
            y0=fvg['low'], y1=fvg['high'],
            fillcolor="rgba(33, 150, 243, 0.1)",
            line=dict(color="rgba(33, 150, 243, 0.6)", width=1, dash='dot'),
            layer='below', row=1, col=1
        )

    for fvg in fvgs.get('bearish', [])[-5:]:
        fig.add_shape(
            type="rect", x0=fvg['timestamp'], x1=df.index[-1],
            y0=fvg['low'], y1=fvg['high'],
            fillcolor="rgba(255, 152, 0, 0.1)",
            line=dict(color="rgba(255, 152, 0, 0.6)", width=1, dash='dot'),
            layer='below', row=1, col=1
        )

    # Fibonacci Golden Pocket
    if 'swing_high' in df.columns and 'swing_low' in df.columns:
        swing_highs = df[df['swing_high']]['high']
        swing_lows = df[df['swing_low']]['low']

        if len(swing_highs) > 0 and len(swing_lows) > 0:
            recent_high = swing_highs.iloc[-5:].max()
            recent_low = swing_lows.iloc[-5:].min()

            # FIXED BUG #15: In strong trends, recent_low can be > recent_high
            # (e.g., recent swing lows higher than old swing highs in uptrend)
            fib_levels = None
            if recent_high > recent_low:
                fib_levels = FibonacciAnalyzer.calculate_retracements(recent_high, recent_low, 'bullish')
            else:
                # Use broader range when swing points are inverted
                recent_high = df['high'].iloc[-100:].max()
                recent_low = df['low'].iloc[-100:].min()
                if recent_high > recent_low:
                    fib_levels = FibonacciAnalyzer.calculate_retracements(recent_high, recent_low, 'bullish')

            # Only draw if we have valid Fibonacci levels
            if fib_levels is not None:
                # Golden Pocket
                fig.add_shape(
                    type="rect", x0=df.index[0], x1=df.index[-1],
                    y0=fib_levels['78.6%'], y1=fib_levels['61.8%'],
                    fillcolor="rgba(255, 215, 0, 0.08)",
                    line=dict(width=0), layer='below', row=1, col=1
                )

                # Key levels
                for level_name, color in [
                    ('61.8%', '#ffd700'), ('78.6%', '#ffd700'), ('50%', '#ff00ff')
                ]:
                    fig.add_hline(
                        y=fib_levels[level_name], line_dash="dash",
                        line_color=color, line_width=1, opacity=0.4,
                        annotation_text=f"Fib {level_name}",
                        annotation_position="right", row=1, col=1
                    )

    # Trading Signals
    if signals:
        long_signals = [s for s in signals if s['type'] == 'LONG']
        short_signals = [s for s in signals if s['type'] == 'SHORT']

        if long_signals:
            fig.add_trace(
                go.Scatter(
                    x=[s['timestamp'] for s in long_signals],
                    y=[s['entry_price'] for s in long_signals],
                    mode='markers+text',
                    name='LONG',
                    marker=dict(
                        symbol='triangle-up',
                        size=[s['confidence'] * 4 for s in long_signals],
                        color='#00ff00',
                        line=dict(color='#ffffff', width=2)
                    ),
                    text=['L'] * len(long_signals),
                    textposition='bottom center',
                    textfont=dict(size=10, color='#00ff00')
                ),
                row=1, col=1
            )

        if short_signals:
            fig.add_trace(
                go.Scatter(
                    x=[s['timestamp'] for s in short_signals],
                    y=[s['entry_price'] for s in short_signals],
                    mode='markers+text',
                    name='SHORT',
                    marker=dict(
                        symbol='triangle-down',
                        size=[s['confidence'] * 4 for s in short_signals],
                        color='#ff0000',
                        line=dict(color='#ffffff', width=2)
                    ),
                    text=['S'] * len(short_signals),
                    textposition='top center',
                    textfont=dict(size=10, color='#ff0000')
                ),
                row=1, col=1
            )

    # Layout
    fig.update_layout(
        template='plotly_dark',
        height=700,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="left", x=0)
    )

    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="Price (USDT)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig

# Main app
def main():
    # Status indicator
    status_placeholder = st.empty()
    status_placeholder.info("🔄 Loading market data...")

    # Update config
    Config.TIMEFRAME = timeframe
    Config.LOOKBACK_BARS = lookback_bars
    Config.MIN_CONFLUENCE_SCORE = min_confluence
    Config.RISK_PER_TRADE = risk_per_trade / 100
    Config.LEVERAGE = leverage

    # Fetch data
    df, htf_df, status = fetch_market_data(data_source, timeframe, lookback_bars)

    if df is None:
        status_placeholder.error(f"❌ {status}")
        st.stop()

    status_placeholder.success(f"✅ Loaded {len(df)} candles | Last update: {datetime.now().strftime('%H:%M:%S')}")

    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    current_price = df['close'].iloc[-1]
    price_change = ((df['close'].iloc[-1] - df['close'].iloc[-24]) / df['close'].iloc[-24] * 100) if len(df) >= 24 else 0

    with col1:
        st.metric("Current Price", f"${current_price:,.2f}", f"{price_change:+.2f}%")

    with col2:
        st.metric("24h High", f"${df['high'].iloc[-24:].max():,.2f}")

    with col3:
        st.metric("24h Low", f"${df['low'].iloc[-24:].min():,.2f}")

    with col4:
        st.metric("Volume", f"{df['volume'].iloc[-24:].sum():,.0f}")

    with col5:
        session_time = datetime.now()
        hour = session_time.hour
        if 8 <= hour < 10:
            session = "🇬🇧 London"
        elif 13 <= hour <= 15:
            session = "🇺🇸 New York"
        else:
            session = "🌏 Asian"
        st.metric("Session", session)

    # Generate signals
    with st.spinner("🧠 Analyzing Smart Money patterns..."):
        generator = SignalGenerator(df, htf_df)
        signals = generator.generate_signals()

        if signals:
            signals = RiskManager.add_risk_metrics(signals, account_balance)

    # Signals summary
    col1, col2, col3, col4 = st.columns(4)

    long_signals = [s for s in signals if s['type'] == 'LONG'] if signals else []
    short_signals = [s for s in signals if s['type'] == 'SHORT'] if signals else []

    with col1:
        st.metric("Total Signals", len(signals))
    with col2:
        st.metric("🟢 LONG", len(long_signals))
    with col3:
        st.metric("🔴 SHORT", len(short_signals))
    with col4:
        avg_confidence = sum(s['confidence'] for s in signals) / len(signals) if signals else 0
        st.metric("Avg Confidence", f"{avg_confidence:.1f}/6")

    # Chart
    st.markdown("### 📈 Live Chart with Smart Money Analysis")
    chart_fig = create_live_chart(df, signals, generator.order_blocks, generator.fvgs)
    st.plotly_chart(chart_fig, use_container_width=True)

    # Recent signals table
    if signals:
        st.markdown("### 🎯 Recent Trading Signals")

        # Show last 10 signals
        recent_signals = sorted(signals, key=lambda x: x['timestamp'], reverse=True)[:10]

        signal_data = []
        for sig in recent_signals:
            # FIXED BUG #16: Only show '...' if there are actually more than 2 factors
            factors_display = ', '.join(sig['factors'][:2])
            if len(sig['factors']) > 2:
                factors_display += '...'

            signal_data.append({
                'Time': sig['timestamp'].strftime('%Y-%m-%d %H:%M'),
                'Type': sig['type'],
                'Entry': f"${sig['entry_price']:,.2f}",
                'SL': f"${sig['stop_loss']:,.2f}",
                'TP': f"${sig['take_profit']:,.2f}",
                'Confidence': f"{sig['confidence']}/6 {'⭐' * sig['confidence']}",
                'R:R': f"1:{sig['risk_reward']:.2f}",
                'Session': sig.get('session', 'N/A'),
                'Factors': factors_display
            })

        signal_df = pd.DataFrame(signal_data)

        # Color code by type
        def highlight_type(row):
            if row['Type'] == 'LONG':
                return ['background-color: rgba(38, 166, 154, 0.2)'] * len(row)
            else:
                return ['background-color: rgba(239, 83, 80, 0.2)'] * len(row)

        st.dataframe(
            signal_df.style.apply(highlight_type, axis=1),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("⏳ No signals detected with current confluence settings. Try lowering the minimum confluence score.")

    # Smart Money Concepts detected
    with st.expander("🔍 Smart Money Patterns Detected", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Order Blocks**")
            st.write(f"🟢 Bullish: {len(generator.order_blocks['bullish'])}")
            st.write(f"🔴 Bearish: {len(generator.order_blocks['bearish'])}")

        with col2:
            st.markdown("**Fair Value Gaps**")
            st.write(f"🟢 Bullish: {len(generator.fvgs['bullish'])}")
            st.write(f"🔴 Bearish: {len(generator.fvgs['bearish'])}")

        if 'liquidity_sweep' in df.columns:
            sweeps = df['liquidity_sweep'].notna().sum()
            st.write(f"💧 **Liquidity Sweeps:** {sweeps}")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888;'>
        <p><b>⚠️ Risk Warning:</b> This is for educational purposes only. Cryptocurrency trading carries significant risk.</p>
        <p>Strategy: Smart Money Concepts (ICT) • Fibonacci Golden Pocket • Multi-Timeframe Confluence</p>
    </div>
    """, unsafe_allow_html=True)

    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
