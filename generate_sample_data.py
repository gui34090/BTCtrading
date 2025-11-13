#!/usr/bin/env python3
"""
Generate sample BTC/USDT data for testing the trading system
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_realistic_btc_data(num_candles=500, start_price=95000):
    """
    Generate realistic BTC price data with trends, reversals, and volatility

    Args:
        num_candles: Number of 15-minute candles to generate
        start_price: Starting BTC price

    Returns:
        DataFrame with OHLCV data
    """

    # Set random seed for reproducibility
    np.random.seed(42)

    # Initialize
    timestamps = []
    opens, highs, lows, closes, volumes = [], [], [], [], []

    current_time = datetime.now() - timedelta(minutes=15 * num_candles)
    current_price = start_price

    # Simulate different market phases
    trend_direction = 1  # 1 = bullish, -1 = bearish
    trend_strength = 0.0005
    volatility = 0.003

    for i in range(num_candles):
        # Add timestamp
        timestamps.append(current_time)
        current_time += timedelta(minutes=15)

        # Create market phases (trends and reversals)
        if i % 50 == 0:  # Change trend every 50 candles
            trend_direction *= -1
            trend_strength = np.random.uniform(0.0003, 0.001)

        # Increase volatility during trend changes
        if i % 50 < 5:
            current_volatility = volatility * 2
        else:
            current_volatility = volatility

        # Generate candle
        open_price = current_price

        # Random walk with trend
        price_change = trend_direction * trend_strength + np.random.normal(0, current_volatility)
        close_price = open_price * (1 + price_change)

        # Generate high and low
        wick_size = np.random.uniform(0.001, 0.005)
        high_price = max(open_price, close_price) * (1 + wick_size)
        low_price = min(open_price, close_price) * (1 - wick_size)

        # Sometimes create strong wicks (liquidity sweeps)
        if np.random.random() < 0.05:  # 5% chance
            if np.random.random() < 0.5:
                low_price = low_price * 0.995  # Deep wick down
            else:
                high_price = high_price * 1.005  # Deep wick up

        # Volume (correlated with price movement)
        base_volume = 1000
        volume_multiplier = 1 + abs(price_change) * 50
        volume = base_volume * volume_multiplier * np.random.uniform(0.8, 1.2)

        # Store
        opens.append(open_price)
        highs.append(high_price)
        lows.append(low_price)
        closes.append(close_price)
        volumes.append(volume)

        # Update current price
        current_price = close_price

    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    })

    return df

if __name__ == "__main__":
    print("Generating sample BTC/USDT data...")

    # Generate 15-minute data (500 candles = ~5 days)
    df = generate_realistic_btc_data(num_candles=500, start_price=95000)

    # Save to CSV
    filename = 'sample_btc_usdt_15m.csv'
    df.to_csv(filename, index=False)

    print(f"✓ Generated {len(df)} candles")
    print(f"✓ Date range: {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    print(f"✓ Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
    print(f"✓ Saved to: {filename}")
    print("\nFirst few rows:")
    print(df.head())
    print("\nLast few rows:")
    print(df.tail())
