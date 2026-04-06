# Backtrader Benchmark

This benchmark application demonstrates a simple Moving Average Crossover strategy using Backtrader.

## Strategy Details

- **Entry Signal**: SMA(50) crosses above SMA(500)
- **Exit Signal**: SMA(50) crosses below SMA(500)
- **Quantity**: 1 BTC per trade
- **Initial Balance**: 10,000,000 USD
- **Commission**: 0.1% (10 basis points)
- **Data**: BTCUSDT 1-minute data from Jan 1, 2024 to Dec 31, 2024

## Running the Benchmark

The easiest way to run the benchmark is using the provided shell script:

```bash
./run_benchmark.sh
```

This will run the benchmark with default settings. You can add options:

```bash
./run_benchmark.sh --verbose --plot
```

### Direct UV Execution

You can also run directly with UV:

```bash
uv run benchmark.py --data ../../data/BTCUSDT.csv
```

### Available Options

- `--capital <amount>`: Set initial capital (default: 10,000,000 USD)
- `--commission <rate>`: Set commission rate (default: 0.001 or 0.1%)
- `--plot`: Enable plotting of results (warning: can be slow with large datasets)
- `--verbose`: Enable verbose logging (slows down execution)
- `--debug`: Print debug information about CSV structure

## Performance Metrics

The benchmark outputs:
- Execution time
- Final portfolio value
- Profit/Loss
- Return percentage
- Sharpe ratio
- Maximum drawdown
- Total trades and win rate
