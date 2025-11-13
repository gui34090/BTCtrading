#!/usr/bin/env python3
"""
Advanced Pattern Detection & Volume Analysis
=============================================

Enhancements for Smart Money trading system:
- Volume confirmation and spike detection
- False breakout pattern identification
- Run on stops cascade detection
- Volume climax identification
- Nested Fibonacci multi-timeframe alignment

Author: Institutional Trading System
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# ============================================================================
# VOLUME ANALYZER
# ============================================================================

class VolumeAnalyzer:
    """Advanced volume analysis for signal confirmation"""

    @staticmethod
    def calculate_volume_profile(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Calculate volume metrics

        Args:
            df: OHLCV DataFrame
            period: Lookback period for calculations

        Returns:
            DataFrame with volume indicators
        """
        df = df.copy()

        # Volume Moving Average
        df['volume_ma'] = df['volume'].rolling(window=period).mean()

        # Volume Standard Deviation
        df['volume_std'] = df['volume'].rolling(window=period).std()

        # Volume Z-Score (normalized volume)
        df['volume_zscore'] = (df['volume'] - df['volume_ma']) / df['volume_std']

        # Relative Volume (current / average)
        df['relative_volume'] = df['volume'] / df['volume_ma']

        # Volume Spike Detection (> 2 standard deviations)
        df['volume_spike'] = df['volume_zscore'] > 2.0

        # Volume Climax (extreme spike > 3 std devs)
        df['volume_climax'] = df['volume_zscore'] > 3.0

        # On-Balance Volume (OBV)
        df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()

        # Volume-Weighted Average Price (VWAP)
        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

        return df

    @staticmethod
    def detect_volume_confirmation(df: pd.DataFrame, idx: int, direction: str) -> Tuple[bool, float, str]:
        """
        Check if volume confirms a signal

        Args:
            df: DataFrame with volume indicators
            idx: Index to check
            direction: 'long' or 'short'

        Returns:
            Tuple of (is_confirmed, confidence_boost, description)
        """
        if idx >= len(df) or 'relative_volume' not in df.columns:
            return False, 0.0, "No volume data"

        row = df.iloc[idx]

        # Strong volume spike (> 2x average)
        if row.get('relative_volume', 1.0) > 2.0:
            if row.get('volume_spike', False):
                return True, 1.0, f"Strong volume spike ({row['relative_volume']:.1f}x avg)"

        # Moderate volume increase (> 1.5x average)
        elif row.get('relative_volume', 1.0) > 1.5:
            return True, 0.5, f"Moderate volume increase ({row['relative_volume']:.1f}x avg)"

        # Check OBV alignment
        if idx > 0:
            obv_direction = 'up' if row.get('obv', 0) > df.iloc[idx-1].get('obv', 0) else 'down'

            if direction == 'long' and obv_direction == 'up':
                return True, 0.3, "OBV confirms bullish momentum"
            elif direction == 'short' and obv_direction == 'down':
                return True, 0.3, "OBV confirms bearish momentum"

        return False, 0.0, "No volume confirmation"

    @staticmethod
    def detect_volume_climax(df: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
        """
        Identify volume climax points (potential reversals)

        A volume climax occurs when:
        - Extreme volume spike (> 3x average)
        - Often marks exhaustion/reversal points

        Args:
            df: DataFrame with volume data
            lookback: Bars to look back

        Returns:
            DataFrame with climax markers
        """
        df = df.copy()

        if 'volume_climax' not in df.columns:
            df = VolumeAnalyzer.calculate_volume_profile(df)

        # Climax is when volume spike coincides with price exhaustion
        df['bullish_climax'] = (
            (df['volume_climax']) &
            (df['close'] < df['open']) &  # Red candle
            (df['low'] == df['low'].rolling(lookback).min())  # New low
        )

        df['bearish_climax'] = (
            (df['volume_climax']) &
            (df['close'] > df['open']) &  # Green candle
            (df['high'] == df['high'].rolling(lookback).max())  # New high
        )

        return df


# ============================================================================
# FALSE BREAKOUT DETECTOR
# ============================================================================

class FalseBreakoutDetector:
    """Detect engineered liquidity via false breakouts"""

    @staticmethod
    def detect_long_wicks(df: pd.DataFrame, wick_ratio: float = 0.6) -> pd.DataFrame:
        """
        Identify candles with long wicks (potential false breakouts)

        Args:
            df: OHLCV DataFrame
            wick_ratio: Minimum ratio of wick to body

        Returns:
            DataFrame with wick markers
        """
        df = df.copy()

        # Calculate body and wicks
        df['body'] = abs(df['close'] - df['open'])
        df['upper_wick'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_wick'] = df[['open', 'close']].min(axis=1) - df['low']

        # Long upper wick (bearish rejection)
        df['long_upper_wick'] = (
            (df['upper_wick'] / df['body'] > wick_ratio) &
            (df['body'] > 0)  # Avoid division by zero
        )

        # Long lower wick (bullish rejection)
        df['long_lower_wick'] = (
            (df['lower_wick'] / df['body'] > wick_ratio) &
            (df['body'] > 0)
        )

        # Pin bar (both wicks long)
        df['pin_bar'] = df['long_upper_wick'] | df['long_lower_wick']

        return df

    @staticmethod
    def detect_failed_breakout(df: pd.DataFrame, lookback: int = 10) -> pd.DataFrame:
        """
        Detect failed breakout patterns

        A failed breakout occurs when:
        1. Price breaks above resistance (or below support)
        2. Quickly reverses back inside range
        3. Often with long wick

        Args:
            df: OHLCV DataFrame with swing points
            lookback: Bars to define resistance/support

        Returns:
            DataFrame with failed breakout markers
        """
        df = df.copy()

        # Calculate recent highs and lows
        df['resistance'] = df['high'].rolling(window=lookback).max()
        df['support'] = df['low'].rolling(window=lookback).min()

        # Detect breakout attempts
        df['break_above'] = df['high'] > df['resistance'].shift(1)
        df['break_below'] = df['low'] < df['support'].shift(1)

        # Failed breakout: breaks level but closes inside
        df['failed_breakout_bearish'] = (
            df['break_above'] &
            (df['close'] < df['resistance'].shift(1))
        )

        df['failed_breakout_bullish'] = (
            df['break_below'] &
            (df['close'] > df['support'].shift(1))
        )

        # Combined failed breakout signal
        df['failed_breakout'] = df['failed_breakout_bearish'] | df['failed_breakout_bullish']

        return df


# ============================================================================
# RUN ON STOPS DETECTOR
# ============================================================================

class RunOnStopsDetector:
    """Detect cascading stop loss events"""

    @staticmethod
    def detect_stop_cascade(df: pd.DataFrame, threshold_move: float = 0.02,
                           volume_multiplier: float = 2.0) -> pd.DataFrame:
        """
        Identify "run on stops" - rapid cascading price moves

        Characteristics:
        - Rapid price movement (> 2% in short time)
        - High volume spike
        - Multiple swing levels broken quickly

        Args:
            df: OHLCV DataFrame with volume data
            threshold_move: Minimum % move to qualify
            volume_multiplier: Volume spike threshold

        Returns:
            DataFrame with cascade markers
        """
        df = df.copy()

        # Ensure volume profile exists
        if 'relative_volume' not in df.columns:
            df = VolumeAnalyzer.calculate_volume_profile(df)

        # Calculate rapid price moves
        df['price_change_3bar'] = df['close'].pct_change(periods=3).abs()
        df['price_change_5bar'] = df['close'].pct_change(periods=5).abs()

        # Bullish cascade (upward)
        df['bullish_cascade'] = (
            (df['price_change_3bar'] > threshold_move) &
            (df['close'] > df['open']) &  # Green candle
            (df['relative_volume'] > volume_multiplier)
        )

        # Bearish cascade (downward)
        df['bearish_cascade'] = (
            (df['price_change_3bar'] > threshold_move) &
            (df['close'] < df['open']) &  # Red candle
            (df['relative_volume'] > volume_multiplier)
        )

        # Combined cascade signal
        df['stop_cascade'] = df['bullish_cascade'] | df['bearish_cascade']

        # Count levels broken
        df['levels_broken'] = 0
        if 'swing_high' in df.columns and 'swing_low' in df.columns:
            # Simple approximation
            for i in range(5, len(df)):
                recent_highs = df['high'].iloc[i-5:i][df['swing_high'].iloc[i-5:i]].values
                recent_lows = df['low'].iloc[i-5:i][df['swing_low'].iloc[i-5:i]].values

                levels_broken_up = np.sum(df['high'].iloc[i] > recent_highs)
                levels_broken_down = np.sum(df['low'].iloc[i] < recent_lows)

                df.loc[df.index[i], 'levels_broken'] = max(levels_broken_up, levels_broken_down)

        return df

    @staticmethod
    def identify_exhaustion(df: pd.DataFrame, idx: int) -> Tuple[bool, str]:
        """
        Check if a stop cascade shows signs of exhaustion

        Args:
            df: DataFrame with cascade data
            idx: Index to check

        Returns:
            Tuple of (is_exhausted, description)
        """
        if idx >= len(df) - 1:
            return False, "Not enough data"

        current = df.iloc[idx]
        next_bar = df.iloc[idx + 1]

        # Check for volume climax
        if current.get('volume_climax', False):
            # Price reversal after climax?
            if current.get('bullish_cascade', False) and next_bar['close'] < next_bar['open']:
                return True, "Bullish cascade exhausted - bearish reversal"
            elif current.get('bearish_cascade', False) and next_bar['close'] > next_bar['open']:
                return True, "Bearish cascade exhausted - bullish reversal"

        return False, "No exhaustion signals"


# ============================================================================
# NESTED FIBONACCI ANALYZER
# ============================================================================

class NestedFibonacciAnalyzer:
    """Multi-timeframe Fibonacci confluence (Russian Doll strategy)"""

    @staticmethod
    def calculate_multi_timeframe_fibs(dfs: Dict[str, pd.DataFrame],
                                      timeframes: List[str]) -> Dict:
        """
        Calculate Fibonacci levels across multiple timeframes

        Args:
            dfs: Dictionary of DataFrames {timeframe: df}
            timeframes: List of timeframe names (e.g., ['15m', '1h', '4h'])

        Returns:
            Dictionary of nested Fibonacci zones
        """
        fib_zones = {}

        for tf in timeframes:
            if tf not in dfs:
                continue

            df = dfs[tf]

            # Find recent swing high/low
            swing_highs = df[df.get('swing_high', False)]
            swing_lows = df[df.get('swing_low', False)]

            if len(swing_highs) > 0 and len(swing_lows) > 0:
                recent_high = swing_highs['high'].iloc[-5:].max()
                recent_low = swing_lows['low'].iloc[-5:].min()

                # Calculate Fibonacci levels
                diff = recent_high - recent_low
                fib_zones[tf] = {
                    '0%': recent_low,
                    '23.6%': recent_low + diff * 0.236,
                    '38.2%': recent_low + diff * 0.382,
                    '50%': recent_low + diff * 0.5,
                    '61.8%': recent_low + diff * 0.618,
                    '78.6%': recent_low + diff * 0.786,
                    '100%': recent_high
                }

        return fib_zones

    @staticmethod
    def find_confluence_zones(fib_zones: Dict, tolerance: float = 0.005) -> List[Dict]:
        """
        Find price zones where multiple timeframe Fibonacci levels align

        Args:
            fib_zones: Dictionary from calculate_multi_timeframe_fibs()
            tolerance: Price tolerance for confluence (0.5% default)

        Returns:
            List of confluence zones with metadata
        """
        confluence_zones = []

        # Get all unique price levels
        all_levels = []
        for tf, levels in fib_zones.items():
            for fib_name, price in levels.items():
                all_levels.append({
                    'timeframe': tf,
                    'fib_level': fib_name,
                    'price': price
                })

        # Sort by price
        all_levels.sort(key=lambda x: x['price'])

        # Find clusters
        i = 0
        while i < len(all_levels):
            cluster = [all_levels[i]]
            base_price = all_levels[i]['price']

            # Look for nearby levels
            j = i + 1
            while j < len(all_levels):
                if abs(all_levels[j]['price'] - base_price) / base_price <= tolerance:
                    cluster.append(all_levels[j])
                    j += 1
                else:
                    break

            # If cluster has multiple timeframes, it's a confluence zone
            unique_timeframes = len(set(item['timeframe'] for item in cluster))

            if unique_timeframes >= 2:  # At least 2 different timeframes
                avg_price = np.mean([item['price'] for item in cluster])
                confluence_zones.append({
                    'price': avg_price,
                    'timeframes': unique_timeframes,
                    'levels': cluster,
                    'strength': unique_timeframes * len(cluster)  # Higher = stronger
                })

            i = max(j, i + 1)

        # Sort by strength
        confluence_zones.sort(key=lambda x: x['strength'], reverse=True)

        return confluence_zones

    @staticmethod
    def is_in_confluence_zone(price: float, confluence_zones: List[Dict],
                              tolerance: float = 0.005) -> Tuple[bool, Optional[Dict]]:
        """
        Check if price is within a Fibonacci confluence zone

        Args:
            price: Current price to check
            confluence_zones: List from find_confluence_zones()
            tolerance: Price tolerance

        Returns:
            Tuple of (is_in_zone, zone_details)
        """
        for zone in confluence_zones:
            if abs(price - zone['price']) / zone['price'] <= tolerance:
                return True, zone

        return False, None


# ============================================================================
# INTEGRATED PATTERN ANALYZER
# ============================================================================

class IntegratedPatternAnalyzer:
    """Combines all advanced pattern detection"""

    def __init__(self, df: pd.DataFrame):
        """Initialize with OHLCV data"""
        self.df = df.copy()
        self._enrich_data()

    def _enrich_data(self):
        """Add all advanced indicators"""
        # Volume analysis
        self.df = VolumeAnalyzer.calculate_volume_profile(self.df)

        # False breakouts
        self.df = FalseBreakoutDetector.detect_long_wicks(self.df)
        self.df = FalseBreakoutDetector.detect_failed_breakout(self.df)

        # Stop cascades
        self.df = RunOnStopsDetector.detect_stop_cascade(self.df)

        # Volume climax
        self.df = VolumeAnalyzer.detect_volume_climax(self.df)

    def get_enhanced_confluence(self, idx: int, direction: str) -> Tuple[int, List[str]]:
        """
        Calculate enhanced confluence score including volume and patterns

        Args:
            idx: DataFrame index
            direction: 'long' or 'short'

        Returns:
            Tuple of (additional_score, additional_factors)
        """
        score = 0
        factors = []

        if idx >= len(self.df):
            return score, factors

        row = self.df.iloc[idx]

        # Volume confirmation
        is_confirmed, boost, description = VolumeAnalyzer.detect_volume_confirmation(
            self.df, idx, direction
        )
        if is_confirmed:
            score += 1
            factors.append(f"Volume: {description}")

        # False breakout (bullish reversal for longs)
        if direction == 'long' and row.get('failed_breakout_bullish', False):
            score += 1
            factors.append("Failed Breakout (Bullish)")

        elif direction == 'short' and row.get('failed_breakout_bearish', False):
            score += 1
            factors.append("Failed Breakout (Bearish)")

        # Long wick rejection
        if direction == 'long' and row.get('long_lower_wick', False):
            score += 1
            factors.append("Long Lower Wick (Rejection)")

        elif direction == 'short' and row.get('long_upper_wick', False):
            score += 1
            factors.append("Long Upper Wick (Rejection)")

        # Stop cascade exhaustion
        if row.get('stop_cascade', False):
            is_exhausted, exhaustion_desc = RunOnStopsDetector.identify_exhaustion(self.df, idx)
            if is_exhausted:
                score += 1
                factors.append("Stop Cascade Exhaustion")

        return score, factors

    def get_data(self) -> pd.DataFrame:
        """Return enriched DataFrame"""
        return self.df


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_advanced_analysis(df: pd.DataFrame, latest_idx: int = -1):
    """Print advanced pattern analysis for latest candle"""
    if latest_idx == -1:
        latest_idx = len(df) - 1

    row = df.iloc[latest_idx]

    print("\n" + "="*60)
    print("ADVANCED PATTERN ANALYSIS")
    print("="*60)

    # Volume analysis
    if 'relative_volume' in df.columns:
        print(f"Volume: {row.get('relative_volume', 1.0):.2f}x average", end="")
        if row.get('volume_spike', False):
            print(" ⚡ SPIKE", end="")
        if row.get('volume_climax', False):
            print(" 💥 CLIMAX", end="")
        print()

    # Pattern detection
    patterns_detected = []

    if row.get('failed_breakout', False):
        patterns_detected.append("Failed Breakout")

    if row.get('long_upper_wick', False):
        patterns_detected.append("Long Upper Wick")

    if row.get('long_lower_wick', False):
        patterns_detected.append("Long Lower Wick")

    if row.get('stop_cascade', False):
        patterns_detected.append("Stop Cascade")

    if patterns_detected:
        print(f"Patterns: {', '.join(patterns_detected)}")
    else:
        print("Patterns: None detected")

    print("="*60 + "\n")
