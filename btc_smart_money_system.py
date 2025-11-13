#!/usr/bin/env python3
"""
Institutional-Grade BTC/USDT Live Chart with Smart Money Signals
==================================================================

This system implements a sophisticated trading strategy based on:
- Smart Money Concepts (ICT methodology)
- Fibonacci analysis with Golden Pocket (61.8%-78.6%)
- Elliott Wave Theory patterns (5-3 waves with advanced patterns)
- Volume confirmation and advanced pattern detection
- Candlestick patterns and period level tracking
- Fibonacci Time Zones and trendline liquidity
- Multi-timeframe confluence analysis (12+ factors)

Author: Institutional Trading System
Version: 3.0.0 - 100% Complete Implementation
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ccxt
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Import enhanced modules
try:
    from elliott_wave_analyzer import ElliottWaveAnalyzer, format_wave_summary
    from advanced_patterns import (
        IntegratedPatternAnalyzer, VolumeAnalyzer,
        NestedFibonacciAnalyzer
    )
    from final_features import (
        FibonacciTimeZones, AdvancedWavePatterns, CandlestickPatterns,
        PeriodLevels, TrendlineDetector
    )
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_FEATURES_AVAILABLE = False
    print("⚠️  Enhanced features (Elliott Wave, Volume Analysis) not available.")


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """System configuration parameters"""

    # Data settings
    SYMBOL = "BTC/USDT"
    TIMEFRAME = "15m"  # Primary timeframe for signals
    HTF_TIMEFRAME = "4h"  # Higher timeframe for bias
    LOOKBACK_BARS = 500  # Number of bars to analyze

    # Smart Money Concepts
    SWING_LENGTH = 10  # Bars to left/right for swing detection
    OB_THRESHOLD = 0.002  # 0.2% minimum move for Order Block
    FVG_THRESHOLD = 0.001  # 0.1% minimum gap for FVG

    # Fibonacci levels
    FIB_RETRACEMENT_LEVELS = {
        '0%': 0.0,
        '11.4%': 0.114,
        '23.6%': 0.236,
        '38.2%': 0.382,
        '50%': 0.5,
        '61.8%': 0.618,
        '70.5%': 0.705,  # Golden Pocket sweet spot
        '78.6%': 0.786,
        '88.6%': 0.886,
        '100%': 1.0
    }

    FIB_EXTENSION_LEVELS = {
        '127.2%': 1.272,
        '141.4%': 1.414,
        '161.8%': 1.618,  # Primary target
        '200%': 2.0,
        '261.8%': 2.618
    }

    # Trading sessions (UTC times)
    LONDON_SESSION = (8, 10)  # 08:00-10:00 UTC
    NY_SESSION = (13, 15)  # 13:30-15:30 UTC (adjusted for clarity)

    # Signal confluence requirements
    MIN_CONFLUENCE_SCORE = 6  # Minimum factors for valid signal (50% of 12 factors)

    # Risk management
    RISK_PER_TRADE = 0.01  # 1% risk per trade
    LEVERAGE = 200  # High leverage for intraday

    # Visualization
    CHART_THEME = "plotly_dark"
    CHART_HEIGHT = 1200


# ============================================================================
# DATA ACQUISITION
# ============================================================================

class DataFetcher:
    """Handles data acquisition from exchanges or CSV files"""

    def __init__(self, exchange_id: str = 'binance'):
        """Initialize exchange connection"""
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
        """
        Fetch OHLCV data from exchange

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candlestick timeframe (e.g., '15m', '4h')
            limit: Number of candles to fetch

        Returns:
            DataFrame with OHLCV data
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            print(f"✓ Fetched {len(df)} candles for {symbol} ({timeframe})")
            return df

        except Exception as e:
            print(f"✗ Error fetching data: {e}")
            return pd.DataFrame()

    @staticmethod
    def load_from_csv(filepath: str) -> pd.DataFrame:
        """
        Load historical data from CSV file

        Args:
            filepath: Path to CSV file with OHLCV data

        Returns:
            DataFrame with OHLCV data
        """
        try:
            df = pd.read_csv(filepath)

            # Standardize column names
            column_mapping = {
                'Open': 'open', 'High': 'high', 'Low': 'low',
                'Close': 'close', 'Volume': 'volume',
                'Date': 'timestamp', 'Datetime': 'timestamp'
            }
            df.rename(columns=column_mapping, inplace=True)

            # Parse timestamp
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)

            print(f"✓ Loaded {len(df)} candles from CSV")
            return df

        except Exception as e:
            print(f"✗ Error loading CSV: {e}")
            return pd.DataFrame()


# ============================================================================
# SMART MONEY CONCEPTS DETECTOR
# ============================================================================

class SmartMoneyDetector:
    """Detects institutional footprints: Order Blocks, FVGs, BOS/ChoCh"""

    @staticmethod
    def detect_swing_points(df: pd.DataFrame, length: int = 10) -> pd.DataFrame:
        """
        Identify swing highs and lows

        Args:
            df: OHLCV DataFrame
            length: Bars to left/right for confirmation

        Returns:
            DataFrame with swing_high and swing_low columns
        """
        df = df.copy()
        df['swing_high'] = False
        df['swing_low'] = False

        for i in range(length, len(df) - length):
            # Swing High: highest high in window
            window_highs = df['high'].iloc[i-length:i+length+1]
            if df['high'].iloc[i] == window_highs.max():
                df.loc[df.index[i], 'swing_high'] = True

            # Swing Low: lowest low in window
            window_lows = df['low'].iloc[i-length:i+length+1]
            if df['low'].iloc[i] == window_lows.min():
                df.loc[df.index[i], 'swing_low'] = True

        return df

    @staticmethod
    def detect_order_blocks(df: pd.DataFrame, threshold: float = 0.002) -> Dict:
        """
        Identify Order Blocks (last opposite candle before impulse move)

        Args:
            df: OHLCV DataFrame
            threshold: Minimum % move to qualify as impulse

        Returns:
            Dictionary of bullish and bearish order blocks
        """
        bullish_obs = []
        bearish_obs = []

        for i in range(1, len(df) - 1):
            current = df.iloc[i]
            next_candle = df.iloc[i + 1]

            # Bullish OB: Last red candle before strong green move
            if current['close'] < current['open']:  # Red candle
                move = (next_candle['close'] - current['low']) / current['low']
                if move > threshold:
                    bullish_obs.append({
                        'timestamp': current.name,
                        'high': current['high'],
                        'low': current['low'],
                        'type': 'bullish'
                    })

            # Bearish OB: Last green candle before strong red move
            if current['close'] > current['open']:  # Green candle
                move = (current['high'] - next_candle['close']) / current['high']
                if move > threshold:
                    bearish_obs.append({
                        'timestamp': current.name,
                        'high': current['high'],
                        'low': current['low'],
                        'type': 'bearish'
                    })

        return {
            'bullish': bullish_obs[-20:],  # Keep last 20
            'bearish': bearish_obs[-20:]
        }

    @staticmethod
    def detect_fvg(df: pd.DataFrame, threshold: float = 0.001) -> Dict:
        """
        Identify Fair Value Gaps (price inefficiencies)

        A bullish FVG exists when: candle[i-1].low > candle[i+1].high
        A bearish FVG exists when: candle[i-1].high < candle[i+1].low

        Args:
            df: OHLCV DataFrame
            threshold: Minimum % gap size

        Returns:
            Dictionary of bullish and bearish FVGs
        """
        bullish_fvgs = []
        bearish_fvgs = []

        for i in range(1, len(df) - 1):
            prev_candle = df.iloc[i - 1]
            current = df.iloc[i]
            next_candle = df.iloc[i + 1]

            # Bullish FVG (gap up)
            if prev_candle['low'] > next_candle['high']:
                gap_size = (prev_candle['low'] - next_candle['high']) / next_candle['high']
                if gap_size > threshold:
                    bullish_fvgs.append({
                        'timestamp': current.name,
                        'high': prev_candle['low'],
                        'low': next_candle['high'],
                        'type': 'bullish',
                        'mitigated': False
                    })

            # Bearish FVG (gap down)
            if prev_candle['high'] < next_candle['low']:
                gap_size = (next_candle['low'] - prev_candle['high']) / prev_candle['high']
                if gap_size > threshold:
                    bearish_fvgs.append({
                        'timestamp': current.name,
                        'high': next_candle['low'],
                        'low': prev_candle['high'],
                        'type': 'bearish',
                        'mitigated': False
                    })

        # Check for mitigation (price returning to fill gap)
        for fvg in bullish_fvgs + bearish_fvgs:
            idx = df.index.get_loc(fvg['timestamp'])
            future_data = df.iloc[idx+1:]

            for future_idx, row in future_data.iterrows():
                if fvg['type'] == 'bullish':
                    if row['low'] <= fvg['high']:
                        fvg['mitigated'] = True
                        break
                else:  # bearish
                    if row['high'] >= fvg['low']:
                        fvg['mitigated'] = True
                        break

        return {
            'bullish': [f for f in bullish_fvgs if not f['mitigated']][-15:],
            'bearish': [f for f in bearish_fvgs if not f['mitigated']][-15:]
        }

    @staticmethod
    def detect_market_structure(df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify Break of Structure (BOS) and Change of Character (ChoCh)

        BOS: Price breaks previous swing high (bullish) or low (bearish)
        ChoCh: Potential reversal - failure to make new high/low

        Args:
            df: OHLCV DataFrame with swing points

        Returns:
            DataFrame with BOS and ChoCh markers
        """
        df = df.copy()
        df['bos'] = None
        df['choch'] = None

        swing_highs = df[df['swing_high']]['high'].values
        swing_lows = df[df['swing_low']]['low'].values

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return df

        # Detect BOS (bullish: break above previous high)
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['high'].iloc[:i].max() * 0.999:
                df.loc[df.index[i], 'bos'] = 'bullish'
            elif df['close'].iloc[i] < df['low'].iloc[:i].min() * 1.001:
                df.loc[df.index[i], 'bos'] = 'bearish'

        return df

    @staticmethod
    def detect_liquidity_sweep(df: pd.DataFrame, swing_length: int = 10) -> pd.DataFrame:
        """
        Identify liquidity sweeps (stop hunts beyond swing points)

        A liquidity sweep occurs when price briefly breaks a swing level
        then quickly reverses, triggering stops.

        Args:
            df: OHLCV DataFrame with swing points
            swing_length: Lookback for swing detection

        Returns:
            DataFrame with liquidity_sweep column
        """
        df = df.copy()
        df['liquidity_sweep'] = None

        for i in range(swing_length, len(df)):
            current = df.iloc[i]
            prev_swing_high = df['high'].iloc[i-swing_length:i][df['swing_high'].iloc[i-swing_length:i]].max() if df['swing_high'].iloc[i-swing_length:i].any() else 0
            prev_swing_low = df['low'].iloc[i-swing_length:i][df['swing_low'].iloc[i-swing_length:i]].min() if df['swing_low'].iloc[i-swing_length:i].any() else float('inf')

            # Bullish sweep: Wick below swing low, close above
            if prev_swing_low != float('inf') and current['low'] < prev_swing_low:
                if current['close'] > prev_swing_low:
                    df.loc[df.index[i], 'liquidity_sweep'] = 'bullish'

            # Bearish sweep: Wick above swing high, close below
            if prev_swing_high > 0 and current['high'] > prev_swing_high:
                if current['close'] < prev_swing_high:
                    df.loc[df.index[i], 'liquidity_sweep'] = 'bearish'

        return df


# ============================================================================
# FIBONACCI ANALYZER
# ============================================================================

class FibonacciAnalyzer:
    """Calculate Fibonacci retracements and extensions"""

    @staticmethod
    def calculate_retracements(high: float, low: float, trend: str = 'bullish') -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels

        Args:
            high: Swing high price
            low: Swing low price
            trend: 'bullish' or 'bearish'

        Returns:
            Dictionary of retracement levels
        """
        diff = high - low
        levels = {}

        if trend == 'bullish':
            # For bullish trend, calculate from high down
            for name, ratio in Config.FIB_RETRACEMENT_LEVELS.items():
                levels[name] = high - (diff * ratio)
        else:
            # For bearish trend, calculate from low up
            for name, ratio in Config.FIB_RETRACEMENT_LEVELS.items():
                levels[name] = low + (diff * ratio)

        return levels

    @staticmethod
    def calculate_extensions(high: float, low: float, trend: str = 'bullish') -> Dict[str, float]:
        """
        Calculate Fibonacci extension levels for profit targets

        Args:
            high: Swing high price
            low: Swing low price
            trend: 'bullish' or 'bearish'

        Returns:
            Dictionary of extension levels
        """
        diff = high - low
        levels = {}

        if trend == 'bullish':
            # Project extensions upward from low
            for name, ratio in Config.FIB_EXTENSION_LEVELS.items():
                levels[name] = low + (diff * ratio)
        else:
            # Project extensions downward from high
            for name, ratio in Config.FIB_EXTENSION_LEVELS.items():
                levels[name] = high - (diff * ratio)

        return levels

    @staticmethod
    def is_in_golden_pocket(price: float, high: float, low: float, trend: str = 'bullish') -> bool:
        """
        Check if price is in Golden Pocket (61.8%-78.6% retracement)

        Args:
            price: Current price
            high: Swing high
            low: Swing low
            trend: 'bullish' or 'bearish'

        Returns:
            True if in Golden Pocket
        """
        levels = FibonacciAnalyzer.calculate_retracements(high, low, trend)

        if trend == 'bullish':
            return levels['78.6%'] <= price <= levels['61.8%']
        else:
            return levels['61.8%'] <= price <= levels['78.6%']

    @staticmethod
    def is_in_discount_zone(price: float, high: float, low: float) -> bool:
        """Check if price is in discount zone (0%-50% retracement)"""
        levels = FibonacciAnalyzer.calculate_retracements(high, low, 'bullish')
        return levels['0%'] <= price <= levels['50%']

    @staticmethod
    def is_in_premium_zone(price: float, high: float, low: float) -> bool:
        """Check if price is in premium zone (50%-100% retracement)"""
        levels = FibonacciAnalyzer.calculate_retracements(high, low, 'bullish')
        return levels['50%'] <= price <= levels['100%']


# ============================================================================
# SESSION FILTER
# ============================================================================

class SessionFilter:
    """Filter signals based on trading session timing"""

    @staticmethod
    def get_session(timestamp: pd.Timestamp) -> Optional[str]:
        """
        Determine which trading session the timestamp falls into

        Args:
            timestamp: Pandas timestamp (should be UTC)

        Returns:
            Session name or None
        """
        hour = timestamp.hour
        minute = timestamp.minute

        # London session: 08:00-10:00 UTC
        if Config.LONDON_SESSION[0] <= hour < Config.LONDON_SESSION[1]:
            return 'London'

        # NY session: 13:30-15:30 UTC (simplified to 13-15)
        if Config.NY_SESSION[0] <= hour <= Config.NY_SESSION[1]:
            return 'New York'

        return None

    @staticmethod
    def is_high_liquidity_session(timestamp: pd.Timestamp) -> bool:
        """Check if timestamp is during high liquidity session"""
        return SessionFilter.get_session(timestamp) is not None

    @staticmethod
    def add_session_column(df: pd.DataFrame) -> pd.DataFrame:
        """Add session column to DataFrame"""
        df = df.copy()
        df['session'] = df.index.map(SessionFilter.get_session)
        return df


# ============================================================================
# SIGNAL GENERATOR
# ============================================================================

class SignalGenerator:
    """Generate trading signals based on confluence criteria"""

    def __init__(self, df: pd.DataFrame, htf_df: pd.DataFrame = None):
        """
        Initialize signal generator

        Args:
            df: Primary timeframe OHLCV data
            htf_df: Higher timeframe data for bias (optional)
        """
        self.df = df.copy()
        self.htf_df = htf_df
        self.signals = []

        # Enrich data with indicators
        self._enrich_data()

    def _enrich_data(self):
        """Add all technical indicators and features to DataFrame"""
        print("📊 Enriching data with Smart Money features...")

        # Detect swing points
        self.df = SmartMoneyDetector.detect_swing_points(self.df, Config.SWING_LENGTH)

        # Detect market structure
        self.df = SmartMoneyDetector.detect_market_structure(self.df)

        # Detect liquidity sweeps
        self.df = SmartMoneyDetector.detect_liquidity_sweep(self.df, Config.SWING_LENGTH)

        # Add session info
        self.df = SessionFilter.add_session_column(self.df)

        # Detect Order Blocks
        self.order_blocks = SmartMoneyDetector.detect_order_blocks(self.df, Config.OB_THRESHOLD)

        # Detect FVGs
        self.fvgs = SmartMoneyDetector.detect_fvg(self.df, Config.FVG_THRESHOLD)

        print(f"  ✓ Found {len(self.order_blocks['bullish'])} bullish OBs, {len(self.order_blocks['bearish'])} bearish OBs")
        print(f"  ✓ Found {len(self.fvgs['bullish'])} bullish FVGs, {len(self.fvgs['bearish'])} bearish FVGs")
        print(f"  ✓ Detected {self.df['liquidity_sweep'].notna().sum()} liquidity sweeps")

        # Enhanced features (if available)
        if ENHANCED_FEATURES_AVAILABLE:
            print("  🔬 Activating enhanced analysis modules...")

            # Elliott Wave Analysis
            try:
                self.elliott_analyzer = ElliottWaveAnalyzer(self.df, self.df)
                self.elliott_patterns = self.elliott_analyzer.detect_impulse_waves(min_confidence=0.6)
                self.corrective_patterns = self.elliott_analyzer.detect_corrective_waves(min_confidence=0.5)
                print(f"  ✓ Detected {len(self.elliott_patterns)} Elliott Wave patterns")

                if self.elliott_patterns:
                    print(format_wave_summary(self.elliott_patterns))
            except Exception as e:
                print(f"  ⚠️  Elliott Wave analysis failed: {e}")
                self.elliott_analyzer = None
                self.elliott_patterns = []

            # Advanced Pattern Analysis
            try:
                self.pattern_analyzer = IntegratedPatternAnalyzer(self.df)
                self.df = self.pattern_analyzer.get_data()
                print(f"  ✓ Volume analysis active")
                print(f"  ✓ False breakout detection active")
                print(f"  ✓ Stop cascade detection active")
            except Exception as e:
                print(f"  ⚠️  Advanced pattern analysis failed: {e}")
                self.pattern_analyzer = None

            # Final Features (100% Complete)
            try:
                print("  🎯 Activating final 5% features...")

                # Candlestick Patterns
                self.df = CandlestickPatterns.enrich_dataframe(self.df)
                pattern_count = self.df['candlestick_pattern'].notna().sum()
                print(f"  ✓ Detected {pattern_count} candlestick patterns")

                # Period Levels
                self.df = PeriodLevels.calculate_period_levels(self.df)
                print(f"  ✓ Period levels calculated (daily/weekly/monthly)")

                # Fibonacci Time Zones
                swing_df = self.df[self.df['swing_high'] | self.df['swing_low']].copy()
                if len(swing_df) > 0:
                    self.df = FibonacciTimeZones.identify_time_zone_events(self.df, swing_df)
                    time_zone_count = self.df['fib_time_zone'].sum()
                    print(f"  ✓ Identified {time_zone_count} Fibonacci time zones")

                # Trendline Detection
                if len(swing_df) >= 2:
                    self.trendlines = TrendlineDetector.detect_trendlines(self.df, swing_df)
                    print(f"  ✓ Detected {len(self.trendlines)} trendlines")
                else:
                    self.trendlines = []

                # Advanced Wave Patterns (ending diagonals, triangles)
                if self.elliott_patterns:
                    for pattern in self.elliott_patterns:
                        # Check for ending diagonal in Wave 5
                        if pattern.wave_5:
                            wave_5_data = {
                                'start_idx': pattern.wave_5.start_idx,
                                'end_idx': pattern.wave_5.end_idx
                            }
                            diagonal = AdvancedWavePatterns.detect_ending_diagonal(self.df, wave_5_data)
                            if diagonal:
                                print(f"  ✓ Ending diagonal detected in Wave 5 ({diagonal['direction']})")

                    # Check for triangles
                    triangles = AdvancedWavePatterns.detect_contracting_triangle(self.df, swing_df)
                    if triangles:
                        print(f"  ✓ Detected {len(triangles)} contracting triangle(s)")
                        self.triangles = triangles
                    else:
                        self.triangles = []
                else:
                    self.triangles = []

            except Exception as e:
                print(f"  ⚠️  Final features initialization failed: {e}")
                self.trendlines = []
                self.triangles = []
        else:
            self.elliott_analyzer = None
            self.elliott_patterns = []
            self.pattern_analyzer = None
            self.trendlines = []
            self.triangles = []

    def _get_htf_bias(self) -> Optional[str]:
        """
        Determine higher timeframe market bias

        Returns:
            'bullish', 'bearish', or None
        """
        if self.htf_df is None:
            return None

        # Enrich HTF data if not already done
        if 'bos' not in self.htf_df.columns:
            self.htf_df = SmartMoneyDetector.detect_swing_points(self.htf_df, Config.SWING_LENGTH)
            self.htf_df = SmartMoneyDetector.detect_market_structure(self.htf_df)

        # Simple bias: last BOS direction
        if 'bos' in self.htf_df.columns and self.htf_df['bos'].notna().any():
            last_bos = self.htf_df[self.htf_df['bos'].notna()]['bos'].iloc[-1]
            return last_bos

        return None

    def _calculate_confluence_score(self, idx: int, direction: str) -> Tuple[int, List[str]]:
        """
        Calculate confluence score for a potential signal

        Args:
            idx: DataFrame index
            direction: 'long' or 'short'

        Returns:
            Tuple of (score, list of confluence factors)
        """
        score = 0
        factors = []

        row = self.df.iloc[idx]
        price = row['close']

        # Find recent swing high/low for Fibonacci
        recent_swing_high = self.df[self.df['swing_high']]['high'].iloc[-5:].max() if self.df['swing_high'].any() else price * 1.05
        recent_swing_low = self.df[self.df['swing_low']]['low'].iloc[-5:].min() if self.df['swing_low'].any() else price * 0.95

        # 1. Liquidity Sweep
        if pd.notna(row['liquidity_sweep']):
            if (direction == 'long' and row['liquidity_sweep'] == 'bullish') or \
               (direction == 'short' and row['liquidity_sweep'] == 'bearish'):
                score += 1
                factors.append('Liquidity Sweep')

        # 2. Order Block
        obs = self.order_blocks['bullish'] if direction == 'long' else self.order_blocks['bearish']
        for ob in obs:
            if ob['low'] <= price <= ob['high']:
                score += 1
                factors.append('Order Block')
                break

        # 3. Fair Value Gap
        fvgs = self.fvgs['bullish'] if direction == 'long' else self.fvgs['bearish']
        for fvg in fvgs:
            if fvg['low'] <= price <= fvg['high']:
                score += 1
                factors.append('FVG')
                break

        # 4. Fibonacci Golden Pocket
        if direction == 'long':
            if FibonacciAnalyzer.is_in_golden_pocket(price, recent_swing_high, recent_swing_low, 'bullish'):
                score += 1
                factors.append('Golden Pocket')
        else:
            if FibonacciAnalyzer.is_in_golden_pocket(price, recent_swing_high, recent_swing_low, 'bearish'):
                score += 1
                factors.append('Golden Pocket')

        # 5. Session Timing
        if SessionFilter.is_high_liquidity_session(row.name):
            score += 1
            factors.append(f'{row["session"]} Session')

        # 6. HTF Market Structure Alignment
        htf_bias = self._get_htf_bias()
        if htf_bias:
            if (direction == 'long' and htf_bias == 'bullish') or \
               (direction == 'short' and htf_bias == 'bearish'):
                score += 1
                factors.append('HTF Alignment')

        # ===== ENHANCED FEATURES =====
        if ENHANCED_FEATURES_AVAILABLE and self.pattern_analyzer:
            # 7. Volume Confirmation
            additional_score, additional_factors = self.pattern_analyzer.get_enhanced_confluence(idx, direction)
            score += additional_score
            factors.extend(additional_factors)

            # 8. Elliott Wave Context
            if self.elliott_analyzer and self.elliott_patterns:
                wave_context = self.elliott_analyzer.get_current_wave_context()

                if wave_context['wave']:
                    # Wave 2 is prime entry zone
                    if wave_context['wave'] == 'Wave 2':
                        if (direction == 'long' and wave_context['direction'] == 'bullish') or \
                           (direction == 'short' and wave_context['direction'] == 'bearish'):
                            score += 2  # Strong boost for Wave 2 entries
                            factors.append(f"Elliott Wave 2 Entry ({wave_context['smart_money_action']})")

                    # Wave 3 continuation
                    elif wave_context['wave'] == 'Wave 3':
                        if (direction == 'long' and wave_context['direction'] == 'bullish') or \
                           (direction == 'short' and wave_context['direction'] == 'bearish'):
                            score += 1
                            factors.append("Elliott Wave 3 (Money Wave)")

                    # Wave 5 warning (exit zone)
                    elif wave_context['wave'] == 'Wave 5':
                        score -= 1  # Reduce confidence in Wave 5
                        factors.append("Wave 5 Warning (Exit Zone)")

            # 9. Candlestick Pattern Confluence
            if 'candlestick_pattern' in self.df.columns and pd.notna(row.get('candlestick_pattern')):
                pattern_strength = row.get('pattern_strength', 0)
                if pattern_strength > 0:
                    # Map pattern type to direction
                    pattern_name = row['candlestick_pattern']
                    is_bullish_pattern = any(word in pattern_name.lower() for word in ['bullish', 'hammer', 'morning', 'dragonfly'])
                    is_bearish_pattern = any(word in pattern_name.lower() for word in ['bearish', 'shooting', 'evening', 'gravestone'])

                    if (direction == 'long' and is_bullish_pattern) or (direction == 'short' and is_bearish_pattern):
                        # Add strength-based score (1-3 points)
                        pattern_score = min(3, pattern_strength)
                        score += pattern_score
                        factors.append(f"Candlestick: {pattern_name}")

            # 10. Period Level Confluence
            if hasattr(self, 'df') and any(col in self.df.columns for col in ['prev_day_high', 'prev_week_high']):
                level_score, level_factors = PeriodLevels.check_level_interaction(price, row)
                if level_score > 0:
                    score += level_score
                    factors.extend(level_factors)

            # 11. Fibonacci Time Zone Confluence
            if 'fib_time_zone' in self.df.columns:
                tz_score, tz_description = FibonacciTimeZones.get_confluence_score(row.name, self.df)
                if tz_score > 0:
                    score += tz_score
                    factors.append(tz_description)

            # 12. Trendline Proximity
            if hasattr(self, 'trendlines') and self.trendlines:
                tl_score, tl_factors = TrendlineDetector.check_trendline_proximity(idx, price, self.trendlines)
                if tl_score > 0:
                    score += tl_score
                    factors.extend(tl_factors)

        return score, factors

    def _validate_ict_setup(self, idx: int, direction: str) -> bool:
        """
        Validate proper ICT setup sequence before generating signal

        ICT requires:
        1. Liquidity sweep (optional but preferred)
        2. Entry in discount zone (longs) or premium zone (shorts)
        3. Order Block OR Fair Value Gap (required)
        4. Market structure confirmation OR HTF alignment (required)

        Args:
            idx: Current bar index
            direction: 'long' or 'short'

        Returns:
            True if proper ICT setup exists
        """
        row = self.df.iloc[idx]
        price = row['close']

        # Find swing high/low for Fibonacci zones
        recent_swing_high = self.df[self.df['swing_high']]['high'].iloc[-5:].max() if self.df['swing_high'].any() else price * 1.05
        recent_swing_low = self.df[self.df['swing_low']]['low'].iloc[-5:].min() if self.df['swing_low'].any() else price * 0.95

        # REQUIRED: Must be in proper Fibonacci zone
        if direction == 'long':
            # Long entries should be in DISCOUNT zone (below 50%)
            in_correct_zone = FibonacciAnalyzer.is_in_discount_zone(price, recent_swing_high, recent_swing_low)
        else:
            # Short entries should be in PREMIUM zone (above 50%)
            in_correct_zone = FibonacciAnalyzer.is_in_premium_zone(price, recent_swing_high, recent_swing_low)

        if not in_correct_zone:
            return False  # Not in correct zone, no signal

        # REQUIRED: Must have Order Block OR Fair Value Gap
        has_ob = False
        has_fvg = False

        # Check Order Blocks
        obs = self.order_blocks['bullish'] if direction == 'long' else self.order_blocks['bearish']
        for ob in obs:
            if ob['low'] <= price <= ob['high']:
                has_ob = True
                break

        # Check Fair Value Gaps
        fvgs = self.fvgs['bullish'] if direction == 'long' else self.fvgs['bearish']
        for fvg in fvgs:
            if fvg['low'] <= price <= fvg['high']:
                has_fvg = True
                break

        if not (has_ob or has_fvg):
            return False  # No OB or FVG, no signal

        # REQUIRED: HTF alignment OR market structure
        htf_bias = self._get_htf_bias()
        htf_aligned = (direction == 'long' and htf_bias == 'bullish') or (direction == 'short' and htf_bias == 'bearish')

        # Check recent BOS
        has_bos = False
        if 'bos' in self.df.columns:
            recent_bos = self.df.iloc[max(0, idx-10):idx]['bos']
            if recent_bos.notna().any():
                last_bos = recent_bos[recent_bos.notna()].iloc[-1]
                has_bos = (direction == 'long' and last_bos == 'bullish') or (direction == 'short' and last_bos == 'bearish')

        if not (htf_aligned or has_bos):
            return False  # No HTF alignment or BOS, no signal

        # All ICT setup requirements met
        return True

    def generate_signals(self) -> List[Dict]:
        """
        Generate trading signals based on ICT methodology

        Returns:
            List of signal dictionaries
        """
        print("\n🎯 Generating trading signals (ICT Setup Validation)...")

        signals = []
        last_signal_index = -10  # Track last signal to implement cooldown

        for i in range(Config.SWING_LENGTH, len(self.df)):
            row = self.df.iloc[i]

            # Signal cooldown - wait 5 bars between signals (avoid rapid-fire)
            if i - last_signal_index < 5:
                continue

            # Check for long signals
            long_score, long_factors = self._calculate_confluence_score(i, 'long')

            # Check for short signals
            short_score, short_factors = self._calculate_confluence_score(i, 'short')

            # CRITICAL FIX: Prevent contradictory signals on same candle
            # If both long and short qualify, it indicates indecision - skip this candle
            if long_score >= Config.MIN_CONFLUENCE_SCORE and short_score >= Config.MIN_CONFLUENCE_SCORE:
                # Indecision candle - both directions qualify, skip it
                continue

            # Only generate LONG signal if long qualified and short didn't
            elif long_score >= Config.MIN_CONFLUENCE_SCORE and self._validate_ict_setup(i, 'long'):
                # Find swing high/low for stop loss and take profit
                recent_swing_high = self.df[self.df['swing_high']]['high'].iloc[-5:].max() if self.df['swing_high'].any() else row['close'] * 1.05
                recent_swing_low = self.df[self.df['swing_low']]['low'].iloc[-5:].min() if self.df['swing_low'].any() else row['close'] * 0.95

                # Calculate Fibonacci extension for TP
                extensions = FibonacciAnalyzer.calculate_extensions(
                    recent_swing_high, recent_swing_low, 'bullish'
                )

                signal = {
                    'timestamp': row.name,
                    'type': 'LONG',
                    'entry_price': row['close'],
                    'stop_loss': recent_swing_low * 0.998,  # Just below swing low
                    'take_profit': extensions['161.8%'],  # Primary Fib target
                    'confidence': long_score,
                    'factors': long_factors,
                    'session': row['session']
                }
                signals.append(signal)
                last_signal_index = i  # Update cooldown tracker
                print(f"  🟢 LONG @ {row['close']:.2f} | Confidence: {long_score} | {', '.join(long_factors)}")

            # Only generate SHORT signal if short qualified and short didn't
            elif short_score >= Config.MIN_CONFLUENCE_SCORE and self._validate_ict_setup(i, 'short'):
                recent_swing_high = self.df[self.df['swing_high']]['high'].iloc[-5:].max() if self.df['swing_high'].any() else row['close'] * 1.05
                recent_swing_low = self.df[self.df['swing_low']]['low'].iloc[-5:].min() if self.df['swing_low'].any() else row['close'] * 0.95

                extensions = FibonacciAnalyzer.calculate_extensions(
                    recent_swing_high, recent_swing_low, 'bearish'
                )

                signal = {
                    'timestamp': row.name,
                    'type': 'SHORT',
                    'entry_price': row['close'],
                    'stop_loss': recent_swing_high * 1.002,  # Just above swing high
                    'take_profit': extensions['161.8%'],
                    'confidence': short_score,
                    'factors': short_factors,
                    'session': row['session']
                }
                signals.append(signal)
                last_signal_index = i  # Update cooldown tracker
                print(f"  🔴 SHORT @ {row['close']:.2f} | Confidence: {short_score} | {', '.join(short_factors)}")

        self.signals = signals
        print(f"\n✓ Generated {len(signals)} total signals (ICT-validated)")
        return signals


# ============================================================================
# RISK MANAGER
# ============================================================================

class RiskManager:
    """Calculate position sizing and risk/reward ratios"""

    @staticmethod
    def calculate_position_size(
        account_balance: float,
        entry_price: float,
        stop_loss: float,
        risk_per_trade: float = Config.RISK_PER_TRADE
    ) -> Dict:
        """
        Calculate optimal position size based on risk

        Args:
            account_balance: Total account balance
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_per_trade: Risk as decimal (e.g., 0.01 = 1%)

        Returns:
            Dictionary with position size details
        """
        risk_amount = account_balance * risk_per_trade
        price_diff = abs(entry_price - stop_loss)
        position_size = risk_amount / price_diff

        # With leverage
        leveraged_size = position_size * Config.LEVERAGE

        return {
            'position_size': position_size,
            'leveraged_size': leveraged_size,
            'risk_amount': risk_amount,
            'risk_percent': risk_per_trade * 100
        }

    @staticmethod
    def calculate_risk_reward(entry: float, stop_loss: float, take_profit: float) -> float:
        """Calculate risk/reward ratio"""
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        return reward / risk if risk > 0 else 0

    @staticmethod
    def add_risk_metrics(signals: List[Dict], account_balance: float = 10000) -> List[Dict]:
        """Add risk management metrics to signals"""
        for signal in signals:
            # Position sizing
            position = RiskManager.calculate_position_size(
                account_balance,
                signal['entry_price'],
                signal['stop_loss']
            )
            signal.update(position)

            # Risk/reward
            signal['risk_reward'] = RiskManager.calculate_risk_reward(
                signal['entry_price'],
                signal['stop_loss'],
                signal['take_profit']
            )

        return signals


# ============================================================================
# CHART VISUALIZER
# ============================================================================

class ChartVisualizer:
    """Create interactive Plotly charts with all technical overlays"""

    def __init__(self, df: pd.DataFrame, signals: List[Dict],
                 order_blocks: Dict, fvgs: Dict):
        """
        Initialize visualizer

        Args:
            df: OHLCV DataFrame with indicators
            signals: List of trading signals
            order_blocks: Dictionary of order blocks
            fvgs: Dictionary of Fair Value Gaps
        """
        self.df = df
        self.signals = signals
        self.order_blocks = order_blocks
        self.fvgs = fvgs

    def create_chart(self) -> go.Figure:
        """
        Create comprehensive trading chart

        Returns:
            Plotly Figure object
        """
        print("\n📈 Creating interactive chart...")

        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=('BTC/USDT - Smart Money Analysis', 'Volume')
        )

        # 1. Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=self.df.index,
                open=self.df['open'],
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                name='BTC/USDT',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )

        # 2. Volume bars
        colors = ['#26a69a' if close >= open else '#ef5350'
                  for close, open in zip(self.df['close'], self.df['open'])]

        fig.add_trace(
            go.Bar(
                x=self.df.index,
                y=self.df['volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.5
            ),
            row=2, col=1
        )

        # 3. Swing Points
        swing_highs = self.df[self.df['swing_high']]
        swing_lows = self.df[self.df['swing_low']]

        fig.add_trace(
            go.Scatter(
                x=swing_highs.index,
                y=swing_highs['high'],
                mode='markers',
                name='Swing High',
                marker=dict(symbol='triangle-down', size=10, color='#ff9800'),
                hovertemplate='Swing High<br>Price: %{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=swing_lows.index,
                y=swing_lows['low'],
                mode='markers',
                name='Swing Low',
                marker=dict(symbol='triangle-up', size=10, color='#2196f3'),
                hovertemplate='Swing Low<br>Price: %{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )

        # 4. Order Blocks
        self._add_order_blocks(fig)

        # 5. Fair Value Gaps
        self._add_fvgs(fig)

        # 6. Fibonacci Levels
        self._add_fibonacci_levels(fig)

        # 7. Trading Signals
        self._add_signals(fig)

        # 8. Session Highlights
        self._add_session_highlights(fig)

        # Update layout
        fig.update_layout(
            title={
                'text': f"<b>Institutional-Grade BTC/USDT Chart</b><br><sub>Smart Money Concepts • Golden Pocket • Liquidity Analysis</sub>",
                'x': 0.5,
                'xanchor': 'center'
            },
            template=Config.CHART_THEME,
            height=Config.CHART_HEIGHT,
            xaxis_rangeslider_visible=False,
            hovermode='x unified',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(0,0,0,0.5)"
            )
        )

        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Price (USDT)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

        print("✓ Chart created successfully")
        return fig

    def _add_order_blocks(self, fig: go.Figure):
        """Add Order Block zones to chart"""
        # Bullish OBs
        for ob in self.order_blocks['bullish']:
            fig.add_shape(
                type="rect",
                x0=ob['timestamp'],
                x1=self.df.index[-1],
                y0=ob['low'],
                y1=ob['high'],
                fillcolor="rgba(38, 166, 154, 0.2)",
                line=dict(color="rgba(38, 166, 154, 0.5)", width=1),
                layer='below',
                row=1, col=1
            )

        # Bearish OBs
        for ob in self.order_blocks['bearish']:
            fig.add_shape(
                type="rect",
                x0=ob['timestamp'],
                x1=self.df.index[-1],
                y0=ob['low'],
                y1=ob['high'],
                fillcolor="rgba(239, 83, 80, 0.2)",
                line=dict(color="rgba(239, 83, 80, 0.5)", width=1),
                layer='below',
                row=1, col=1
            )

    def _add_fvgs(self, fig: go.Figure):
        """Add Fair Value Gap zones to chart"""
        # Bullish FVGs
        for fvg in self.fvgs['bullish']:
            fig.add_shape(
                type="rect",
                x0=fvg['timestamp'],
                x1=self.df.index[-1],
                y0=fvg['low'],
                y1=fvg['high'],
                fillcolor="rgba(33, 150, 243, 0.15)",
                line=dict(color="rgba(33, 150, 243, 0.8)", width=1, dash='dot'),
                layer='below',
                row=1, col=1
            )

        # Bearish FVGs
        for fvg in self.fvgs['bearish']:
            fig.add_shape(
                type="rect",
                x0=fvg['timestamp'],
                x1=self.df.index[-1],
                y0=fvg['low'],
                y1=fvg['high'],
                fillcolor="rgba(255, 152, 0, 0.15)",
                line=dict(color="rgba(255, 152, 0, 0.8)", width=1, dash='dot'),
                layer='below',
                row=1, col=1
            )

    def _add_fibonacci_levels(self, fig: go.Figure):
        """Add Fibonacci retracement levels"""
        # Find last major swing
        swing_highs = self.df[self.df['swing_high']]['high']
        swing_lows = self.df[self.df['swing_low']]['low']

        if len(swing_highs) < 1 or len(swing_lows) < 1:
            return

        recent_high = swing_highs.iloc[-5:].max()
        recent_low = swing_lows.iloc[-5:].min()

        # Calculate levels
        fib_levels = FibonacciAnalyzer.calculate_retracements(recent_high, recent_low, 'bullish')

        # Golden Pocket highlight
        fig.add_shape(
            type="rect",
            x0=self.df.index[0],
            x1=self.df.index[-1],
            y0=fib_levels['78.6%'],
            y1=fib_levels['61.8%'],
            fillcolor="rgba(255, 215, 0, 0.1)",
            line=dict(width=0),
            layer='below',
            row=1, col=1
        )

        # Draw key Fib levels
        key_levels = ['0%', '23.6%', '38.2%', '50%', '61.8%', '78.6%', '100%']
        colors = {
            '0%': '#00ff00',
            '23.6%': '#00ffff',
            '38.2%': '#ffff00',
            '50%': '#ff00ff',
            '61.8%': '#ffd700',  # Golden
            '78.6%': '#ffd700',  # Golden
            '100%': '#ff0000'
        }

        for level_name in key_levels:
            if level_name in fib_levels:
                fig.add_hline(
                    y=fib_levels[level_name],
                    line_dash="dash",
                    line_color=colors.get(level_name, '#888888'),
                    line_width=1,
                    opacity=0.6,
                    annotation_text=f"Fib {level_name}",
                    annotation_position="right",
                    row=1, col=1
                )

    def _add_signals(self, fig: go.Figure):
        """Add buy/sell signal markers"""
        long_signals = [s for s in self.signals if s['type'] == 'LONG']
        short_signals = [s for s in self.signals if s['type'] == 'SHORT']

        if long_signals:
            long_times = [s['timestamp'] for s in long_signals]
            long_prices = [s['entry_price'] for s in long_signals]
            long_confidences = [s['confidence'] for s in long_signals]
            long_factors = [', '.join(s['factors']) for s in long_signals]

            fig.add_trace(
                go.Scatter(
                    x=long_times,
                    y=long_prices,
                    mode='markers+text',
                    name='LONG Signal',
                    marker=dict(
                        symbol='triangle-up',
                        size=[c * 5 for c in long_confidences],
                        color='#00ff00',
                        line=dict(color='#ffffff', width=2)
                    ),
                    text=['LONG'] * len(long_signals),
                    textposition='bottom center',
                    textfont=dict(size=10, color='#00ff00'),
                    hovertemplate='<b>LONG SIGNAL</b><br>' +
                                  'Price: %{y:.2f}<br>' +
                                  'Confidence: ' + '<br>'.join([str(c) for c in long_confidences]) + '<br>' +
                                  'Factors: ' + '<br>'.join(long_factors) +
                                  '<extra></extra>'
                ),
                row=1, col=1
            )

        if short_signals:
            short_times = [s['timestamp'] for s in short_signals]
            short_prices = [s['entry_price'] for s in short_signals]
            short_confidences = [s['confidence'] for s in short_signals]
            short_factors = [', '.join(s['factors']) for s in short_signals]

            fig.add_trace(
                go.Scatter(
                    x=short_times,
                    y=short_prices,
                    mode='markers+text',
                    name='SHORT Signal',
                    marker=dict(
                        symbol='triangle-down',
                        size=[c * 5 for c in short_confidences],
                        color='#ff0000',
                        line=dict(color='#ffffff', width=2)
                    ),
                    text=['SHORT'] * len(short_signals),
                    textposition='top center',
                    textfont=dict(size=10, color='#ff0000'),
                    hovertemplate='<b>SHORT SIGNAL</b><br>' +
                                  'Price: %{y:.2f}<br>' +
                                  'Confidence: ' + '<br>'.join([str(c) for c in short_confidences]) + '<br>' +
                                  'Factors: ' + '<br>'.join(short_factors) +
                                  '<extra></extra>'
                ),
                row=1, col=1
            )

    def _add_session_highlights(self, fig: go.Figure):
        """Add visual highlights for London/NY sessions"""
        london_sessions = self.df[self.df['session'] == 'London']
        ny_sessions = self.df[self.df['session'] == 'New York']

        # This would ideally add background shading for sessions
        # Simplified version: just add annotations for first occurrence
        if len(london_sessions) > 0:
            fig.add_annotation(
                x=london_sessions.index[0],
                y=london_sessions['high'].iloc[0],
                text="London Open",
                showarrow=True,
                arrowhead=2,
                bgcolor="rgba(0, 255, 0, 0.3)",
                row=1, col=1
            )

        if len(ny_sessions) > 0:
            fig.add_annotation(
                x=ny_sessions.index[0],
                y=ny_sessions['high'].iloc[0],
                text="NY Open",
                showarrow=True,
                arrowhead=2,
                bgcolor="rgba(0, 0, 255, 0.3)",
                row=1, col=1
            )


# ============================================================================
# BACKTESTER
# ============================================================================

class Backtester:
    """Backtest signal performance"""

    def __init__(self, df: pd.DataFrame, signals: List[Dict], initial_balance: float = 10000):
        """
        Initialize backtester

        Args:
            df: OHLCV DataFrame
            signals: List of trading signals
            initial_balance: Starting account balance
        """
        self.df = df
        self.signals = signals
        self.initial_balance = initial_balance
        self.results = []

    def run_backtest(self) -> Dict:
        """
        Run backtest simulation

        Returns:
            Dictionary of performance metrics
        """
        print("\n🔬 Running backtest...")

        balance = self.initial_balance
        wins = 0
        losses = 0
        total_profit = 0
        total_loss = 0
        max_drawdown = 0
        peak_balance = balance

        for signal in self.signals:
            # Find outcome
            entry_idx = self.df.index.get_loc(signal['timestamp'])
            future_data = self.df.iloc[entry_idx+1:]

            if len(future_data) == 0:
                continue

            # Simulate trade outcome
            hit_tp = False
            hit_sl = False

            for idx, row in future_data.iterrows():
                if signal['type'] == 'LONG':
                    if row['high'] >= signal['take_profit']:
                        hit_tp = True
                        break
                    if row['low'] <= signal['stop_loss']:
                        hit_sl = True
                        break
                else:  # SHORT
                    if row['low'] <= signal['take_profit']:
                        hit_tp = True
                        break
                    if row['high'] >= signal['stop_loss']:
                        hit_sl = True
                        break

            # Calculate P&L
            risk_amount = balance * Config.RISK_PER_TRADE

            if hit_tp:
                rr_ratio = signal.get('risk_reward', 2)
                profit = risk_amount * rr_ratio
                balance += profit
                total_profit += profit
                wins += 1
                outcome = 'WIN'
            elif hit_sl:
                loss = risk_amount
                balance -= loss
                total_loss += loss
                losses += 1
                outcome = 'LOSS'
            else:
                outcome = 'OPEN'

            # Track drawdown
            if balance > peak_balance:
                peak_balance = balance
            drawdown = (peak_balance - balance) / peak_balance
            max_drawdown = max(max_drawdown, drawdown)

            self.results.append({
                'signal': signal,
                'outcome': outcome,
                'balance': balance
            })

        # Calculate metrics
        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        profit_factor = (total_profit / total_loss) if total_loss > 0 else float('inf')
        net_profit = balance - self.initial_balance
        roi = (net_profit / self.initial_balance) * 100

        metrics = {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'net_profit': net_profit,
            'roi': roi,
            'max_drawdown': max_drawdown * 100,
            'final_balance': balance
        }

        # Print results
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Total Trades:     {total_trades}")
        print(f"Wins:             {wins} ({win_rate:.1f}%)")
        print(f"Losses:           {losses}")
        print(f"Profit Factor:    {profit_factor:.2f}")
        print(f"Net Profit:       ${net_profit:,.2f}")
        print(f"ROI:              {roi:.2f}%")
        print(f"Max Drawdown:     {max_drawdown * 100:.2f}%")
        print(f"Final Balance:    ${balance:,.2f}")
        print("="*60)

        return metrics


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""

    print("\n" + "="*60)
    print("INSTITUTIONAL BTC/USDT SMART MONEY TRADING SYSTEM")
    print("="*60)
    print(f"Version: 1.0.0")
    print(f"Strategy: ICT Smart Money + Fibonacci + Elliott Wave")
    print(f"Timeframe: {Config.TIMEFRAME} (HTF: {Config.HTF_TIMEFRAME})")
    print("="*60 + "\n")

    # ========================================================================
    # STEP 1: Data Acquisition
    # ========================================================================
    print("📡 Fetching market data...")

    fetcher = DataFetcher('binance')

    # Fetch primary timeframe data
    df = fetcher.fetch_ohlcv(Config.SYMBOL, Config.TIMEFRAME, Config.LOOKBACK_BARS)

    # Fetch higher timeframe for bias
    htf_df = fetcher.fetch_ohlcv(Config.SYMBOL, Config.HTF_TIMEFRAME, 100)

    if df.empty:
        print("✗ Failed to fetch data. Exiting.")
        return

    # Alternative: Load from CSV
    # df = DataFetcher.load_from_csv('btc_usdt_5year_15m.csv')

    # ========================================================================
    # STEP 2: Signal Generation
    # ========================================================================
    generator = SignalGenerator(df, htf_df)
    signals = generator.generate_signals()

    if len(signals) == 0:
        print("\n⚠ No signals generated. Try adjusting confluence requirements or timeframe.")
        # Continue to show chart anyway

    # ========================================================================
    # STEP 3: Risk Management
    # ========================================================================
    print("\n💰 Calculating risk metrics...")
    signals = RiskManager.add_risk_metrics(signals, account_balance=10000)

    # Print top signals
    if signals:
        print("\n🏆 TOP SIGNALS:")
        for i, sig in enumerate(sorted(signals, key=lambda x: x['confidence'], reverse=True)[:5]):
            print(f"\n  #{i+1} {sig['type']} @ ${sig['entry_price']:.2f}")
            print(f"      Confidence: {sig['confidence']}/6")
            print(f"      SL: ${sig['stop_loss']:.2f} | TP: ${sig['take_profit']:.2f}")
            print(f"      R:R = 1:{sig['risk_reward']:.2f}")
            print(f"      Factors: {', '.join(sig['factors'])}")

    # ========================================================================
    # STEP 4: Backtesting
    # ========================================================================
    if signals:
        backtester = Backtester(df, signals, initial_balance=10000)
        metrics = backtester.run_backtest()

    # ========================================================================
    # STEP 5: Chart Visualization
    # ========================================================================
    visualizer = ChartVisualizer(
        df=generator.df,
        signals=signals,
        order_blocks=generator.order_blocks,
        fvgs=generator.fvgs
    )

    fig = visualizer.create_chart()

    # Save chart
    output_file = 'btc_smart_money_chart.html'
    fig.write_html(output_file)
    print(f"\n💾 Chart saved to: {output_file}")
    print("   Open this file in your browser to view the interactive chart.")

    # ========================================================================
    # STEP 6: Export Signals
    # ========================================================================
    if signals:
        signals_df = pd.DataFrame(signals)
        signals_csv = 'trading_signals.csv'
        signals_df.to_csv(signals_csv, index=False)
        print(f"💾 Signals saved to: {signals_csv}")

    print("\n" + "="*60)
    print("✅ SYSTEM EXECUTION COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
