#!/usr/bin/env python
import argparse
import asyncio
import time
import pandas as pd
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path

import basana as bs
from basana.core.enums import OrderOperation, Position
from basana.core.pair import Pair
from basana.backtesting.exchange import Exchange
from basana.core.event_sources.trading_signal import TradingSignal


class SMACrossoverStrategy(bs.TradingSignalSource):
    """
    Simple Moving Average crossover strategy.
    - Enter long when SMA(50) crosses above SMA(500)
    - Exit long when SMA(50) crosses below SMA(500)
    """
    def __init__(self, dispatcher, pair):
        super().__init__(dispatcher)
        self.pair = pair
        self.prices = []
        self.sma_fast = None
        self.sma_slow = None
        self.position = Position.NEUTRAL
        self.bar_dates = []

    async def on_bar_event(self, bar_event):
        # Extract bar data
        bar = bar_event.bar
        
        # Only process bars for our pair
        if bar.pair != self.pair:
            return
        
        # Store price and date
        self.bar_dates.append(bar_event.when)
        self.prices.append(float(bar.close))
        
        # Wait until we have enough data to calculate both SMAs
        if len(self.prices) < 500:
            return
        
        # Calculate SMAs
        prices_series = pd.Series(self.prices)
        self.sma_fast = prices_series.rolling(window=50).mean().iloc[-1]
        self.sma_slow = prices_series.rolling(window=500).mean().iloc[-1]
        
        # Trading logic
        if self.sma_fast > self.sma_slow and self.position == Position.NEUTRAL:
            # Buy signal
            self.position = Position.LONG
            signal = TradingSignal(bar_event.when, Position.LONG, self.pair)
            self.push(signal)
            
        elif self.sma_fast < self.sma_slow and self.position == Position.LONG:
            # Sell signal
            self.position = Position.NEUTRAL
            signal = TradingSignal(bar_event.when, Position.NEUTRAL, self.pair)
            self.push(signal)


class PortfolioManager:
    """Handles portfolio management and order execution."""
    
    def __init__(self, exchange, pair, position_size=Decimal("1")):
        self.exchange = exchange
        self.pair = pair
        self.position_size = position_size
        self.position = Position.NEUTRAL
        self.trades = []
        self.last_price = None
        self.total_pnl = Decimal("0")
    
    async def on_trading_signal(self, signal):
        """React to trading signals by creating orders."""
        # Enter long position
        if signal.position == Position.LONG and self.position == Position.NEUTRAL:
            try:
                order = await self.exchange.create_market_order(
                    operation=OrderOperation.BUY,
                    pair=self.pair,
                    amount=self.position_size
                )
                self.position = Position.LONG
                self.trades.append((signal.when, "BUY", self.position_size, self.last_price))
                print(f"BUY order executed at {self.last_price}")
            except Exception as e:
                print(f"Error executing BUY order: {e}")
        
        # Exit position
        elif signal.position == Position.NEUTRAL and self.position == Position.LONG:
            try:
                order = await self.exchange.create_market_order(
                    operation=OrderOperation.SELL,
                    pair=self.pair,
                    amount=self.position_size
                )
                self.position = Position.NEUTRAL
                self.trades.append((signal.when, "SELL", self.position_size, self.last_price))
                print(f"SELL order executed at {self.last_price}")
            except Exception as e:
                print(f"Error executing SELL order: {e}")
    
    async def on_bar_event(self, bar_event):
        """Update last price on each bar."""
        bar = bar_event.bar
        if bar.pair == self.pair:
            self.last_price = float(bar.close)


async def run_backtest(data_path, start_date, end_date):
    """Run the backtest with the SMA crossover strategy."""
    # Create pair for BTC/USDT
    pair = Pair("BTC", "USDT")
    
    # Load data
    df = pd.read_csv(data_path)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter by date range
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    
    # Create backtesting dispatcher
    dispatcher = bs.backtesting_dispatcher()
    
    # Set up the exchange with initial balance of 10M USDT and 0.1% fee
    initial_balances = {"USDT": Decimal("10000000")}
    fee_strategy = bs.backtesting.fees.Percentage(percentage=Decimal("0.1"))
    exchange = Exchange(
        dispatcher=dispatcher,
        initial_balances=initial_balances,
        fee_strategy=fee_strategy
    )
    
    # Set precision for pair
    exchange.set_pair_info(
        pair, 
        bs.core.pair.PairInfo(
            base_precision=8,  # BTC precision
            quote_precision=2  # USDT precision
        )
    )
    
    # Create our strategy
    strategy = SMACrossoverStrategy(dispatcher, pair)
    
    # Create portfolio manager
    portfolio_manager = PortfolioManager(exchange, pair)
    
    # Connect events
    strategy.subscribe_to_trading_signals(portfolio_manager.on_trading_signal)
    
    # Create bar source
    bar_source = bs.core.event.FifoQueueEventSource()
    exchange.add_bar_source(bar_source)
    
    # Subscribe to bar events
    exchange.subscribe_to_bar_events(pair, strategy.on_bar_event)
    exchange.subscribe_to_bar_events(pair, portfolio_manager.on_bar_event)
    
    # Process each row
    for _, row in df.iterrows():
        # Convert timestamp to UTC
        timestamp = row['timestamp'].to_pydatetime().replace(tzinfo=timezone.utc)
        open_price = Decimal(str(row['open']))
        high_price = Decimal(str(row['high']))
        low_price = Decimal(str(row['low']))
        close_price = Decimal(str(row['close']))
        volume = Decimal(str(row['volume']))
        
        # Create a bar event
        bar = bs.core.bar.Bar(
            datetime=timestamp,
            pair=pair,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume
        )
        
        bar_event = bs.core.bar.BarEvent(when=timestamp, bar=bar)
        bar_source.push(bar_event)
    
    # Run the backtest
    await dispatcher.run()
    
    # Get balance after the test
    balance = await exchange.get_balance("USDT")
    
    # Calculate PnL
    pnl = float(balance.total) - 10000000
    
    # Calculate other statistics
    num_trades = len(portfolio_manager.trades)
    win_trades = 0
    loss_trades = 0
    
    if num_trades > 0:
        # Calculate win/loss trades
        for i in range(0, num_trades-1, 2):
            if i+1 < num_trades:  # Make sure we have a pair of trades
                buy_price = portfolio_manager.trades[i][3]
                sell_price = portfolio_manager.trades[i+1][3]
                if sell_price > buy_price:
                    win_trades += 1
                else:
                    loss_trades += 1
    
    # Return results
    return {
        "balance": float(balance.total),
        "pnl": pnl,
        "num_trades": num_trades,
        "win_trades": win_trades,
        "loss_trades": loss_trades,
        "trades": portfolio_manager.trades
    }


async def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="SMA Crossover Strategy Benchmark with Basana")
    parser.add_argument("--data", required=True, help="Path to the CSV file with price data")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    args = parser.parse_args()
    
    data_path = args.data
    start_date = args.start_date
    end_date = args.end_date
    
    print(f"Running backtest on {data_path} from {start_date} to {end_date}")
    
    # Run benchmark
    start_time = time.time()
    results = await run_backtest(data_path, start_date, end_date)
    end_time = time.time()
    
    print("\nBenchmark Results:")
    print(f"  Running time: {end_time - start_time:.3f} seconds")
    print(f"  Final balance: ${results['balance']:.2f}")
    print(f"  PnL: ${results['pnl']:.2f}")
    print(f"  Number of trades: {results['num_trades']}")
    if results['num_trades'] > 0:
        print(f"  Win/Loss ratio: {results['win_trades']}/{results['loss_trades']}")
        print(f"  Win rate: {results['win_trades']/max(1, results['win_trades'] + results['loss_trades']):.2%}")


if __name__ == "__main__":
    asyncio.run(main()) 