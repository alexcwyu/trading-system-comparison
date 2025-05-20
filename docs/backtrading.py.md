# Backtesting.py Benchmark

This document describes the benchmark implementation for [Backtesting.py](https://kernc.github.io/backtesting.py/), a Python framework for backtesting trading strategies.

## Benchmark Setup

The benchmark implements a simple moving average crossover strategy with the following parameters:

- **Strategy**: SMA Crossover
  - **Entry Signal**: SMA(50) > SMA(500)
  - **Exit Signal**: SMA(50) < SMA(500)
- **Initial Capital**: 10M USD
- **Commission**: 10bps (0.1%)
- **Position Size**: 1 BTC per signal
- **Data**: BTCUSDT 1-minute data from January 1, 2024 to December 31, 2024

## Performance Metrics

The benchmark measures the following metrics:

1. **Execution Time**: Time taken to complete the backtest
2. **Return**: Overall return percentage
3. **Sharpe Ratio**: Risk-adjusted return
4. **Maximum Drawdown**: Largest peak-to-trough decline
5. **Number of Trades**: Total number of trades executed
6. **Final Equity**: Final account balance

## Running the Benchmark

To run the benchmark:

```bash
cd trading-system-comparison/samples/backtrading.py
./run_benchmark.sh
```

The script will:
1. Create a virtual environment using UV package manager
2. Install dependencies
3. Run the benchmark
4. Display performance results

## Implementation Details

The benchmark uses the following Backtesting.py features:

- Strategy class for implementing the trading logic
- Indicator function (I) for calculating moving averages
- Position management for entries and exits
- Performance statistics for evaluation

For optimization, the benchmark:
- Loads only the required time period of data
- Uses vectorized operations where possible
- Minimizes logging during execution 