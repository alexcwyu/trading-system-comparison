import argparse
import time
import pandas as pd
from pathlib import Path

from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.objects import Quantity
from nautilus_trader.test_kit.providers import TestInstrumentProvider

class SMACrossoverStrategy:
    def __init__(self, instrument, qty, commission_bps):
        self.instrument = instrument
        self.qty = qty
        self.commission_bps = commission_bps
        self.sma_fast = []
        self.sma_slow = []
        self.prices = []
        self.position = 0
        self.trades = []

    def on_bar(self, bar: Bar):
        price = float(bar.close)
        self.prices.append(price)

        if len(self.prices) >= 500:
            self.sma_fast.append(pd.Series(self.prices).rolling(window=50).mean().iloc[-1])
            self.sma_slow.append(pd.Series(self.prices).rolling(window=500).mean().iloc[-1])
            if self.position == 0:
                # Entry condition
                if self.sma_fast[-1] > self.sma_slow[-1]:
                    self.position = 1
                    self.trades.append((bar.ts_event, price, "BUY"))
            elif self.position == 1:
                # Exit condition
                if self.sma_fast[-1] < self.sma_slow[-1]:
                    self.position = 0
                    self.trades.append((bar.ts_event, price, "SELL"))

def load_data(data_path, start_date, end_date):
    df = pd.read_csv(data_path, parse_dates=['timestamp'])
    df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    return df

def main(args):
    start_time = time.time()
    # Prepare data
    df = load_data(args.data, args.start_date, args.end_date)

    # This existing benchmark measures Nautilus bar model + strategy dispatch;
    # it does not submit orders through BacktestEngine or emulate brokerage fills.
    instrument = TestInstrumentProvider.btcusdt_binance()
    bar_type = BarType.from_str(f"{instrument.id}-1-MINUTE-LAST-EXTERNAL")

    # Create strategy instance
    strat = SMACrossoverStrategy(instrument, qty=1, commission_bps=0.1)

    # Simulate bars through the strategy
    for _, row in df.iterrows():
        timestamp = pd.Timestamp(row['timestamp'])
        bar = Bar(
            bar_type=bar_type,
            open=instrument.make_price(row['open']),
            high=instrument.make_price(row['high']),
            low=instrument.make_price(row['low']),
            close=instrument.make_price(row['close']),
            volume=instrument.make_qty(row['volume']),
            ts_event=timestamp.value,
            ts_init=timestamp.value,
        )
        strat.on_bar(bar)

    # Calculate result
    trades = strat.trades
    pnl = 0
    pos = 0
    last_entry = None
    for t in trades:
        if t[2] == "BUY":
            last_entry = t[1]
            pos = 1
        elif t[2] == "SELL" and last_entry is not None:
            profit = (t[1] - last_entry) * 1
            cost = (last_entry + t[1]) * strat.commission_bps / 10000
            pnl += profit - cost
            pos = 0
            last_entry = None

    end_time = time.time()
    print(f"Benchmark stats:")
    print(f"  # of trades: {len(trades)}")
    print(f"  PnL: {pnl:.2f} USD")
    print(f"  Run time: {end_time - start_time:.3f} sec")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SMA Crossover Benchmark with Nautilus Trader")
    parser.add_argument("--data", required=True, help="CSV file path")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    args = parser.parse_args()
    main(args)
