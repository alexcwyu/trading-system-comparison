#!/usr/bin/env python
# coding: utf-8

"""
Benchmark for VectorBT

Implements a simple Moving Average Crossover strategy:
- Buy signal: SMA(50) crosses above SMA(500)
- Sell signal: SMA(50) crosses below SMA(500)
- Initial balance: 10M USD
- Commission: 0.1% (10bps)
- Position size: 1 BTC per signal
"""

import os
import time
import argparse
import numpy as np
import pandas as pd
from datetime import datetime
import vectorbt as vbt

# Configure paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))

# Disable progress bars for cleaner output - check vectorbt version for compatibility
try:
    vbt.settings.set_option('progress_bar', False)
except AttributeError:
    # For newer versions of vectorbt
    try:
        vbt.settings['progress_bar'] = False
    except (AttributeError, KeyError):
        # If neither works, we'll just continue without setting it
        pass

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='VectorBT benchmark')
    parser.add_argument('--data', type=str, 
                        default=os.path.join(PROJECT_DIR, 'data', 'BTCUSDT_202401.csv'),
                        help='Path to the data file')
    parser.add_argument('--start-date', type=str, default='2024-01-01',
                        help='Start date for filtering data (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default='2024-01-31',
                        help='End date for filtering data (YYYY-MM-DD)')
    parser.add_argument('--cash', type=float, default=10_000_000,
                        help='Initial cash amount')
    parser.add_argument('--commission', type=float, default=0.001,
                        help='Commission rate (e.g., 0.001 for 0.1%)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode with additional output')
    return parser.parse_args()

def load_data(data_file, start_date, end_date):
    """Load and prepare data for vectorbt."""
    print(f"Loading data from {data_file}...")
    
    # Read the CSV file
    df = pd.read_csv(
        data_file,
        parse_dates=['timestamp'],
        index_col='timestamp'
    )
    
    # Convert column names to lowercase
    df.columns = [col.lower() for col in df.columns]
    
    # Filter by date range
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    print(f"Filtering data from {start_date.date()} to {end_date.date()}")
    df = df[(df.index >= start_date) & (df.index <= end_date)]
    
    # Ensure we have all required columns
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in data file")
    
    print(f"Loaded {len(df)} rows of data")
    return df

def create_crossover_signals(fast_ma, slow_ma):
    """Create crossover signals compatible with any vectorbt version."""
    try:
        # First attempt - use crossover parameter if available
        entries = fast_ma.ma_above(slow_ma, crossover=True)
        exits = fast_ma.ma_below(slow_ma, crossover=True)
        return entries, exits
    except (TypeError, AttributeError):
        try:
            # Second attempt - use vectorbt.indicators.nb directly
            entries = fast_ma.ma > slow_ma.ma
            exits = fast_ma.ma < slow_ma.ma
            
            # Calculate crossovers manually
            entries_crossover = entries & ~entries.shift(1, fill_value=False)
            exits_crossover = exits & ~exits.shift(1, fill_value=False)
            return entries_crossover, exits_crossover
        except Exception:
            # Last resort - simplest possible implementation
            fast = fast_ma.ma.values if hasattr(fast_ma, 'ma') else fast_ma.values
            slow = slow_ma.ma.values if hasattr(slow_ma, 'ma') else slow_ma.values
            
            # Convert to pandas Series with the same index as the original data
            fast_series = pd.Series(fast, index=fast_ma.index if hasattr(fast_ma, 'index') else None)
            slow_series = pd.Series(slow, index=slow_ma.index if hasattr(slow_ma, 'index') else None)
            
            # Calculate crossovers
            above = fast_series > slow_series
            below = fast_series < slow_series
            
            entries = above & ~above.shift(1, fill_value=False)
            exits = below & ~below.shift(1, fill_value=False)
            return entries, exits

def run_sma_crossover_strategy(price, init_cash=10_000_000, commission=0.001, debug=False):
    """Run a simple SMA crossover strategy with vectorbt."""
    # Calculate fast and slow moving averages
    fast_ma = vbt.MA.run(price, window=50)
    slow_ma = vbt.MA.run(price, window=500)
    
    # Generate entry and exit signals using crossover-safe method
    entries, exits = create_crossover_signals(fast_ma, slow_ma)
    
    if debug:
        print(f"Generated {entries.sum()} entry signals and {exits.sum()} exit signals")
    
    # Create portfolio - handle different vectorbt versions
    try:
        # First attempt - most modern API
        portfolio = vbt.Portfolio.from_signals(
            price,
            entries,
            exits,
            init_cash=init_cash,
            fees=commission,
            size=1,  # Fixed position size of 1 BTC
            size_type='amount',  # Use amount instead of fixed
            accumulate=False,  # Don't accumulate positions
            cash_sharing=True
        )
    except (TypeError, KeyError, ValueError) as e:
        if debug:
            print(f"First portfolio attempt failed: {e}")
        try:
            # Second attempt - try with size=1 only
            portfolio = vbt.Portfolio.from_signals(
                price,
                entries,
                exits,
                init_cash=init_cash,
                fees=commission,
                size=1,  # Fixed position size of 1 BTC
                accumulate=False,  # Don't accumulate positions
                cash_sharing=True
            )
        except (TypeError, KeyError, ValueError) as e:
            if debug:
                print(f"Second portfolio attempt failed: {e}")
            # Last attempt - simplest call pattern
            portfolio = vbt.Portfolio.from_signals(
                price,
                entries,
                exits,
                init_cash=init_cash,
                fees=commission
            )
    
    if debug:
        # Print detailed information about trades
        print("\nTrade Records:")
        try:
            if hasattr(portfolio, 'trades') and hasattr(portfolio.trades, 'records'):
                print(portfolio.trades.records)
        except Exception as e:
            print(f"Could not print trade records: {e}")
    
    return portfolio

def run_benchmark(data_file, start_date, end_date, cash, commission, debug=False):
    """Run the benchmark and return metrics."""
    # Load data
    t0 = time.time()
    df = load_data(data_file, start_date, end_date)
    price = df['close']
    t1 = time.time()
    print(f"Data loaded in {t1-t0:.2f} seconds")
    
    # Run strategy
    print("Running SMA crossover strategy...")
    start_time = time.time()
    portfolio = run_sma_crossover_strategy(price, cash, commission, debug)
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Calculate metrics
    try:
        stats = portfolio.stats()
    except AttributeError:
        # Handle older vectorbt versions that don't have stats()
        stats = {'total_return': 0.0, 'annual_return': 0.0, 'max_drawdown': 0.0, 'sharpe_ratio': 0.0}
        
        # Try to calculate total return
        try:
            if hasattr(portfolio, 'final_value') and hasattr(portfolio, 'init_cash'):
                stats['total_return'] = (portfolio.final_value / portfolio.init_cash) - 1
            elif hasattr(portfolio, 'value'):
                stats['total_return'] = (portfolio.value.iloc[-1] / portfolio.value.iloc[0]) - 1
        except Exception as e:
            if debug:
                print(f"Could not calculate total return: {e}")
    
    # Print results
    print(f"\nBacktest completed in {execution_time:.2f} seconds")
    print(f"\n--- Summary Statistics ---")
    print(f"Initial Balance: ${cash:,.2f}")
    
    # Get final value from stats if possible
    final_value = cash
    if 'End Value' in stats:
        try:
            final_value = float(stats['End Value'])
        except (ValueError, TypeError):
            if debug:
                print(f"Could not convert End Value to float")
    else:
        try:
            # Try different ways to get final value
            if hasattr(portfolio, 'final_value'):
                final_value = float(portfolio.final_value)
            elif hasattr(portfolio, 'value') and len(portfolio.value) > 0:
                final_value = float(portfolio.value.iloc[-1])
            else:
                # Calculate from return
                final_value = cash * (1 + float(stats.get('total_return', 0)))
                # Or try Total Return [%]
                if 'Total Return [%]' in stats:
                    final_value = cash * (1 + float(stats['Total Return [%]']) / 100)
        except Exception as e:
            if debug:
                print(f"Could not calculate final value: {e}")
    
    print(f"Final Balance: ${final_value:,.2f}")
    
    # Try different ways to get total return
    total_return = 0.0
    if 'total_return' in stats:
        total_return = stats['total_return']
    elif 'Total Return [%]' in stats:
        total_return = float(stats['Total Return [%]']) / 100
    else:
        # Calculate from final value
        total_return = (final_value / cash) - 1
    
    print(f"Total Return: {total_return:.2%}")
    
    # Print additional stats if available
    for stat_key, format_key in [
        ('annual_return', 'Annual Return [%]'), 
        ('max_drawdown', 'Max Drawdown [%]'), 
        ('sharpe_ratio', 'Sharpe Ratio')
    ]:
        if stat_key in stats:
            try:
                value = float(stats[stat_key])
                if 'return' in stat_key or 'drawdown' in stat_key:
                    print(f"{stat_key.replace('_', ' ').title()}: {value:.2%}")
                else:
                    print(f"{stat_key.replace('_', ' ').title()}: {value:.2f}")
            except (ValueError, TypeError):
                pass
        elif format_key in stats:
            try:
                value = float(stats[format_key])
                if 'Return' in format_key or 'Drawdown' in format_key:
                    print(f"{format_key}: {value/100:.2%}")
                else:
                    print(f"{format_key}: {value:.2f}")
            except (ValueError, TypeError):
                pass
    
    # Print trade count if available
    trade_count = 0
    if 'total_trades' in stats:
        trade_count = int(stats['total_trades'])
    elif 'Total Trades' in stats:
        trade_count = int(stats['Total Trades'])
    elif hasattr(portfolio, 'trades'):
        if hasattr(portfolio.trades, 'count'):
            trade_count = int(portfolio.trades.count)
        elif hasattr(portfolio.trades, 'records'):
            trade_count = len(portfolio.trades.records)
    
    print(f"# Trades: {trade_count}")
    
    if debug:
        print("\n--- Detailed Statistics ---")
        try:
            for k, v in stats.items():
                print(f"{k}: {v}")
        except Exception:
            print("Could not print detailed statistics")
    
    return {
        'runtime': execution_time,
        'data_size': len(df),
        'trades': trade_count,
        'return': float(total_return),
        'equity_final': final_value,
        'sharpe': float(stats.get('sharpe_ratio', stats.get('Sharpe Ratio', 0))),
        'max_dd': float(stats.get('max_drawdown', stats.get('Max Drawdown [%]', 0) / 100 if 'Max Drawdown [%]' in stats else 0))
    }

if __name__ == "__main__":
    print("Starting VectorBT benchmark...")
    args = parse_args()
    metrics = run_benchmark(
        args.data, 
        args.start_date, 
        args.end_date,
        args.cash,
        args.commission,
        args.debug
    )
    print("\nBenchmark complete!") 