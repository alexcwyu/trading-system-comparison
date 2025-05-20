#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SMA Crossover Strategy Benchmark for Backtrader
- SMA(50) > SMA(500) for entry
- SMA(50) < SMA(500) for exit
- Initial balance: 10M USD
- Trading 1 BTC per signal
- Default timeframe: Jan 1, 2024 to Jan 31, 2024
"""

import os
import datetime
import time
import backtrader as bt
import pandas as pd
import argparse
import matplotlib.pyplot as plt


class SMACrossoverStrategy(bt.Strategy):
    """Simple Moving Average Crossover Strategy"""
    
    params = (
        ('fast_sma_period', 50),
        ('slow_sma_period', 500),
        ('order_qty', 1),  # Fixed quantity of 1 BTC per order
        ('verbose', False),  # Set to False to disable logging
    )
    
    def __init__(self):
        # Initialize the moving averages
        self.fast_sma = bt.indicators.SMA(self.data.close, period=self.params.fast_sma_period)
        self.slow_sma = bt.indicators.SMA(self.data.close, period=self.params.slow_sma_period)
        
        # Cross signals
        self.buy_signal = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)
        
        # Track orders
        self.order = None
        
    def log(self, txt, dt=None):
        """Logging function - only executed if verbose is True"""
        if self.params.verbose:
            dt = dt or self.datas[0].datetime.datetime(0)
            print(f'{dt.isoformat()} {txt}')
        
    def notify_order(self, order):
        """Called when order status changes"""
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')
                
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order Canceled/Margin/Rejected')
            
        self.order = None
    
    def notify_trade(self, trade):
        """Called when a trade is closed"""
        if not trade.isclosed:
            return
            
        self.log(f'OPERATION PROFIT, GROSS: {trade.pnl:.2f}, NET: {trade.pnlcomm:.2f}')
    
    def next(self):
        """Main strategy logic"""
        # Check if an order is pending
        if self.order:
            return
            
        # Check if we are in the market
        if not self.position:
            # Buy signal: fast SMA crosses above slow SMA
            if self.buy_signal > 0:
                self.log(f'BUY CREATE, {self.data.close[0]:.2f}')
                self.order = self.buy(size=self.params.order_qty)
        
        else:
            # Sell signal: fast SMA crosses below slow SMA
            if self.buy_signal < 0:
                self.log(f'SELL CREATE, {self.data.close[0]:.2f}')
                self.order = self.sell(size=self.params.order_qty)


def prepare_data(data_path, start_date, end_date):
    """Prepare BTC data for backtrader - optimized for speed"""
    print(f"Loading data from {data_path}...")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    df = pd.read_csv(data_path)
    
    # Convert timestamp to datetime efficiently
    if 'timestamp' in df.columns or 'time' in df.columns:
        timestamp_col = 'timestamp' if 'timestamp' in df.columns else 'time'
        
        # Try to determine timestamp format
        sample_ts = df[timestamp_col].iloc[0]
        try:
            # Check if timestamp is numeric (epoch time)
            epoch_time = float(sample_ts)
            if epoch_time > 1e12:  # Milliseconds
                df['datetime'] = pd.to_datetime(df[timestamp_col], unit='ms')
            else:  # Seconds
                df['datetime'] = pd.to_datetime(df[timestamp_col], unit='s')
        except (ValueError, TypeError):
            # If conversion fails, assume it's a datetime string
            df['datetime'] = pd.to_datetime(df[timestamp_col])
    else:
        # Assume first column is datetime
        df['datetime'] = pd.to_datetime(df.iloc[:, 0])
    
    # Filter for the specified date range
    df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
    
    # Ensure required columns with minimal checking
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col not in df.columns:
            col_lower = col.lower()
            matches = [c for c in df.columns if c.lower() == col_lower]
            if matches:
                df[col] = df[matches[0]]
            else:
                df[col] = df.iloc[:, 1] if col != 'volume' else 1000  # Fast fallback
    
    # Set datetime as index
    df.set_index('datetime', inplace=True)
    
    return df


def parse_date(date_str):
    """Parse date string in YYYY-MM-DD format"""
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run SMA Crossover Strategy Benchmark')
    parser.add_argument('--data', type=str, default="../../data/BTCUSDT_202401.csv", 
                        help='Path to BTCUSDT data CSV file')
    parser.add_argument('--start-date', type=parse_date, default='2024-01-01',
                        help='Start date (YYYY-MM-DD format)')
    parser.add_argument('--end-date', type=parse_date, default='2024-01-31',
                        help='End date (YYYY-MM-DD format)')
    parser.add_argument('--capital', type=float, default=10_000_000, 
                        help='Initial capital in USD')
    parser.add_argument('--commission', type=float, default=0.001, 
                        help='Commission rate (default: 0.1%)')
    parser.add_argument('--plot', action='store_true', 
                        help='Plot results (warning: can be slow with large datasets)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging (slows down execution)')
    parser.add_argument('--debug', action='store_true', 
                        help='Debug CSV structure')
    
    args = parser.parse_args()
    
    # Handle default dates if string values are provided
    if isinstance(args.start_date, str):
        args.start_date = parse_date(args.start_date)
    if isinstance(args.end_date, str):
        args.end_date = parse_date(args.end_date)
    
    if not os.path.exists(args.data):
        print(f"Error: Data file not found at {args.data}")
        exit(1)
    
    if args.debug:
        # Debug mode - separate from critical path
        print("Analyzing CSV structure...")
        try:
            preview_df = pd.read_csv(args.data, nrows=5)
            print("CSV columns:", preview_df.columns.tolist())
            print("Sample data:\n", preview_df.head(2))
        except Exception as e:
            print(f"Error reading CSV: {e}")
            exit(1)
    
    # Define cerebro
    cerebro = bt.Cerebro(stdstats=False)  # Disable standard observers for speed
    
    # Add strategy
    cerebro.addstrategy(SMACrossoverStrategy, verbose=args.verbose)
    
    # Set broker parameters
    cerebro.broker.setcash(args.capital)
    cerebro.broker.setcommission(commission=args.commission)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    
    print(f"Loading data from {args.data}...")
    start_data_time = time.time()
    df = prepare_data(args.data, args.start_date, args.end_date)
    end_data_time = time.time()
    print(f"Data loaded: {len(df)} records in {end_data_time - start_data_time:.2f} seconds")
    
    # Create data feed
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,  # Already set as index
    )
    
    # Add data feed to Cerebro
    cerebro.adddata(data)
    
    # Add essential analyzers only
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    # Start measurement
    start_time = time.time()
    
    # Run backtest
    print("Starting backtest...")
    results = cerebro.run()
    
    # End measurement
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Get the strategy instance
    strategy = results[0]
    
    # Print essential results only
    print("\n==== Backtest Results ====")
    print(f"Execution time: {execution_time:.2f} seconds")
    print(f"Final Portfolio Value: ${cerebro.broker.getvalue():,.2f}")
    print(f"Profit/Loss: ${cerebro.broker.getvalue() - args.capital:,.2f}")
    print(f"Return: {(cerebro.broker.getvalue() / args.capital - 1) * 100:.2f}%")
    
    # Minimal metrics calculation
    try:
        sharpe = strategy.analyzers.sharpe.get_analysis()
        drawdown = strategy.analyzers.drawdown.get_analysis()
        trades = strategy.analyzers.trades.get_analysis()
        
        print("\n==== Performance Metrics ====")
        
        # Sharpe Ratio
        sharpe_ratio = 0
        try:
            sharpe_ratio = getattr(sharpe, 'sharperatio', 0)
            print(f"Sharpe Ratio: {sharpe_ratio:.4f}")
        except:
            pass
        
        # Max Drawdown
        try:
            max_dd = getattr(getattr(drawdown, 'max', None), 'drawdown', 0)
            print(f"Max Drawdown: {max_dd * 100:.2f}%")
        except:
            pass
        
        # Total Trades
        try:
            total = getattr(getattr(trades, 'total', None), 'total', 0)
            won = getattr(getattr(trades, 'won', None), 'total', 0)
            print(f"Total Trades: {total}")
            print(f"Won/Lost: {won}/{total - won}")
            if total > 0:
                print(f"Win Rate: {won / total * 100:.2f}%")
        except:
            pass
        
    except Exception as e:
        print(f"Error calculating metrics: {e}")
    
    # Plot if requested
    if args.plot:
        plt.figure(figsize=(12, 8))
        plt.rcParams['figure.facecolor'] = 'white'
        
        # Add minimal observers for plotting
        cerebro.addobserver(bt.observers.BuySell)
        cerebro.addobserver(bt.observers.Value)
        
        print("Generating plot...")
        cerebro.plot(style='candle', barup='green', bardown='red', 
                    plotdist=0.1, grid=True, volume=False) 