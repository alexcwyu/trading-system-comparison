import argparse
import time
import pandas as pd
from pathlib import Path

from nautilus_trader.simulator import SimulationEngine
from nautilus_trader.backtest import BacktestRun
from nautilus_trader.model.caches import InstrumentCache
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.data import Bar
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.objects import Price, Quantity, Side
from nautilus_trader.account import Account
from nautilus_trader.model.enums import AccountType, AccountStatus
from nautilus_trader.execution.orders import MarketOrder
from nautilus_trader.core.datetime import dt_to_unix_nanos
from nautilus_trader.core.config import config_from_dict

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
                    self.trades.append((bar.timestamp, price, "BUY"))
            elif self.position == 1:
                # Exit condition
                if self.sma_fast[-1] < self.sma_slow[-1]:
                    self.position = 0
                    self.trades.append((bar.timestamp, price, "SELL"))

def load_data(data_path, start_date, end_date):
    df = pd.read_csv(data_path, parse_dates=['timestamp'])
    df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    return df

def main(args):
    start_time = time.time()
    # Prepare data
    df = load_data(args.data, args.start_date, args.end_date)

    # Setup initial account
    account = Account(
        account_id="TEST_ACC",
        account_type=AccountType.CASH,
        status=AccountStatus.ACTIVE,
        currency="USD",
        balance=10_000_000,
    )

    # Setup instrument
    instrument_id = InstrumentId("BTCUSD", "BINANCE")
    instrument = Instrument(
        instrument_id=instrument_id,
        base="BTC",
        quote="USD",
        lot_size=1,
        tick_size=0.01,
    )

    # Create strategy instance
    strat = SMACrossoverStrategy(instrument, qty=1, commission_bps=0.1)

    # Simulate bars through the strategy
    for _, row in df.iterrows():
        bar = Bar(
            instrument_id=instrument_id,
            timestamp=dt_to_unix_nanos(row['timestamp']),
            open=Price(float(row['open']), "USD"),
            high=Price(float(row['high']), "USD"),
            low=Price(float(row['low']), "USD"),
            close=Price(float(row['close']), "USD"),
            volume=Quantity(float(row['volume']), "BTC"),
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
            cost = (last_entry + t[1]) * strat.commission_bps / 1000
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
