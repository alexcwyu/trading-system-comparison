# LEAN Trading System

## System Overview

LEAN is a robust, extensible, and open-source algorithmic trading engine developed by QuantConnect. It's designed to provide a consistent, feature-rich platform for quantitative researchers and traders to develop, backtest, and deploy trading strategies across multiple asset classes.

![LEAN Architecture](https://raw.githubusercontent.com/QuantConnect/Lean/master/Documentation/2-Overview-Detailed.png)

### Key Components

LEAN's architecture is organized into distinct components:

1. **Engine** - The core execution system that orchestrates the data flow, algorithm execution, and result handling.
2. **Algorithm** - User-defined trading strategy, containing logic for securities selection, signal generation, and order placement.
3. **Data Feed** - Manages data acquisition, normalization, and delivery to the algorithm.
4. **Transaction Handler** - Processes and manages orders, executions, and portfolio updates.
5. **Result Handler** - Collects, processes, and stores algorithm performance metrics.
6. **Real-time Handler** - Manages scheduled events and real-time notifications.
7. **History Provider** - Provides historical data access for strategy initialization and backtesting.
8. **API** - Interfaces with external services for data acquisition, result storage, and deployment.

### Supported Markets and Instruments

LEAN provides support for multiple asset classes and markets:

- **Equities**: US, international markets
- **Options**: Equity options, index options
- **Futures**: Commodities, financials, indices
- **Forex**: Major, minor, and exotic currency pairs
- **Crypto**: Multiple exchanges and pairs
- **CFDs**: Contracts for difference

### Performance Characteristics

- **Backtesting Speed**: High-performance backtesting engine capable of processing millions of data points per second.
- **Memory Efficiency**: Optimized memory management for handling large datasets and complex strategies.
- **Live Trading**: Low-latency execution suitable for various trading frequencies, from HFT to daily.
- **Scaling**: Designed for cloud deployment and horizontal scaling.

### Dependencies and Requirements

Core dependencies include:

- **.NET Core**: Primary framework (C# implementation)
- **Python**: Support for Python algorithms via integration layer
- **Market Data**: Integrated with various data providers
- **Minimum Hardware**: 8GB RAM, multi-core CPU recommended for complex strategies
- **Storage**: SSD recommended for optimal data access performance

### Quick Start Guide

```csharp
// Example LEAN algorithm in C#
public class BasicTemplateAlgorithm : QCAlgorithm
{
    public override void Initialize()
    {
        // Set start date and cash
        SetStartDate(2018, 1, 1);
        SetEndDate(2018, 12, 31);
        SetCash(100000);
        
        // Add equity to the algorithm
        AddEquity("SPY", Resolution.Daily);
    }

    public override void OnData(Slice data)
    {
        // Simple strategy: if not invested, buy
        if (!Portfolio.Invested)
        {
            SetHoldings("SPY", 1.0);
            Debug("Purchased SPY on " + Time.ToShortDateString());
        }
    }
}
```

Python equivalent:

```python
class BasicTemplateAlgorithm(QCAlgorithm):
    def Initialize(self):
        # Set start date and cash
        self.SetStartDate(2018, 1, 1)
        self.SetEndDate(2018, 12, 31)
        self.SetCash(100000)
        
        # Add equity to the algorithm
        self.AddEquity("SPY", Resolution.Daily)

    def OnData(self, data):
        # Simple strategy: if not invested, buy
        if not self.Portfolio.Invested:
            self.SetHoldings("SPY", 1.0)
            self.Debug(f"Purchased SPY on {self.Time.strftime('%Y-%m-%d')}")
```

For more detailed examples and documentation, refer to the [official LEAN documentation](https://www.lean.io/docs/v2). 