#!/usr/bin/env python
# coding: utf-8

"""
Benchmark for Backtesting.py
"""

import os
import time
import pandas as pd
import numpy as np
import argparse
from datetime import datetime
from backtesting import Backtest, Strategy
from backtesting.test import SMA
from backtesting.lib import crossover

# Configure paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))

# Parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Backtesting.py benchmark')
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
    return parser.parse_args()

# Define our strategy
class SMACrossStrategy(Strategy):
    """
    Simple Moving Average Crossover Strategy
    - Buy when SMA(50) crosses above SMA(500)
    - Sell when SMA(50) crosses below SMA(500)
    """
    def init(self):
        # Precompute indicators for performance
        price = self.data.Close
        self.sma50 = self.I(SMA, price, 50)
        self.sma500 = self.I(SMA, price, 500)
        
    def next(self):
        # For maximum performance, minimize conditionals and operations
        if not self.position and self.sma50 > self.sma500:
            self.buy(size=1)  # Buy 1 BTC
        elif self.position and self.sma50 < self.sma500:
            self.position.close()

def load_data(data_file, start_date, end_date):
    """Load and prepare data for backtesting with optimized performance"""
    print(f"Loading data from {data_file}...")
    
    # Define needed columns to minimize memory usage
    usecols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    
    # Load data with optimized parameters
    df = pd.read_csv(
        data_file,
        usecols=usecols,
        parse_dates=['timestamp']
    )
    
    # Filter for specified date range using optimized timestamp comparison
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    print(f"Filtering data from {start_date.date()} to {end_date.date()}")
    df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    
    # Use optimized column renaming
    df.columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume'] 
    
    # Set index efficiently
    df.set_index('Datetime', inplace=True)
    
    # Convert to appropriate types to save memory
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    df[numeric_columns] = df[numeric_columns].astype(np.float64)
    
    return df

def run_benchmark(data_file, start_date, end_date, cash, commission):
    """Run the benchmark and return metrics"""
    # Load data
    t0 = time.time()
    data = load_data(data_file, start_date, end_date)
    t1 = time.time()
    print(f"Data loaded: {len(data)} bars in {t1-t0:.2f} seconds")
    
    # Initialize backtesting with optimized parameters
    bt = Backtest(
        data,
        SMACrossStrategy,
        cash=cash,
        commission=commission,
        trade_on_close=True,
        exclusive_orders=True
    )
    
    # Measure performance
    print("Running backtest...")
    start_time = time.time()
    results = bt.run()
    end_time = time.time()
    
    # Calculate metrics
    run_time = end_time - start_time
    
    # Print results
    print(f"\nBacktest completed in {run_time:.2f} seconds")
    print(f"\n--- Summary Statistics ---")
    print(f"Initial Balance: ${cash:,.2f}")
    print(f"Final Balance: ${results['Equity Final [$]']:,.2f}")
    print(f"Return: {results['Return [%]']:.2f}%")
    print(f"Sharpe Ratio: {results['Sharpe Ratio']:.2f}")
    print(f"Max Drawdown: {results['Max. Drawdown [%]']:.2f}%")
    print(f"# Trades: {results['# Trades']}")
    
    # Only if debug mode
    if os.environ.get('DEBUG'):
        print("\n--- Detailed Statistics ---")
        print(results)
        
        # Plot results
        bt.plot(
            filename=os.path.join(BASE_DIR, 'backtest_plot.html'),
            open_browser=False,
            plot_width=1200
        )
    
    return {
        'runtime': run_time,
        'data_size': len(data),
        'trades': results['# Trades'],
        'return': results['Return [%]'],
        'equity_final': results['Equity Final [$]'],
        'sharpe': results['Sharpe Ratio'],
        'max_dd': results['Max. Drawdown [%]']
    }

if __name__ == "__main__":
    print("Starting Backtesting.py benchmark...")
    args = parse_args()
    metrics = run_benchmark(
        args.data, 
        args.start_date, 
        args.end_date,
        args.cash,
        args.commission
    )
    print("\nBenchmark complete!") 