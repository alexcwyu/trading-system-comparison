# LiuAlgoTrader Trading System

## Overview

LiuAlgoTrader is a scalable, multi-process, ML-ready framework for algorithmic trading. It employs a producer-consumer design pattern with a focus on high throughput and robust error handling. The framework is designed to be hands-free for strategy developers, handling low-level concerns like connection issues, data processing, and trade execution.

```mermaid
graph TD
    subgraph "Core Components"
        SCR[Scanners]
        PR[Producer]
        CO[Consumers]
        DB[(Database)]
    end
    
    subgraph "Trading Elements"
        STR[Strategies]
        DL[Data Loader]
        TR[Trader]
    end
    
    subgraph "Data Flow"
        DP[Data Provider]
        WS[WebSockets]
        API[REST API]
    end
    
    subgraph "Analytics"
        AN[Analysis]
        ML[Machine Learning]
        MN[Miners]
    end
    
    SCR --> PR
    DP --> PR
    PR --> CO
    CO --> STR
    STR --> TR
    DL --> STR
    TR --> DB
    DB --> AN
    AN --> ML
    MN --> DB
</graph>
```

LiuAlgoTrader implements a producer-consumer architecture where:

1. **Scanners** identify stocks that meet certain criteria
2. A **Producer** process connects to data providers and streams market data
3. Multiple **Consumer** processes receive this data and execute trading strategies
4. **Database** stores all trading operations for analysis and back-testing

## Key Components

### Scanners

Scanners are run periodically to search for stocks from the universe that adhere to specific criteria. Users can easily create and deploy scanners with minimal code. Scanners determine when to subscribe to events of specific stocks.

### Producer

The producer process interacts with data providers via WebSockets, receives market data updates, and distributes them to the appropriate consumer queues. It manages the subscription of new symbols discovered by scanners.

### Consumers

Consumer processes handle the algorithmic decision-making and initiate trades. Each consumer:
- Reads events from its queue
- Processes market data updates
- Executes trading strategies
- Sends orders to the broker
- Tracks positions and order status

### Strategies

Strategies receive stock events from symbols selected by scanners and analyze stock movements using various indicators to decide actions. LiuAlgoTrader supports:
- Both long and short positions
- Day trading and swing trading strategies
- Trading windows configuration
- Custom parameters and callbacks

### Data Loader

The DataLoader class provides a DataFrame-like interface to load historical data or update real-time data from WebSockets, creating a consistent interface across different data providers.

## Supported Markets and Instruments

- US Equities and ETFs (via Alpaca Markets)
- Cryptocurrency (via Gemini)
- Additional markets via Polygon.io data

## Performance Characteristics

LiuAlgoTrader is designed for high throughput, leveraging:
- Python's multiprocessing for parallelism
- Asyncio for cooperative multitasking within processes
- Queue-based inter-process communication
- Load balancing of symbols across consumer processes
- Automatic scaling based on available hardware

Performance metrics tracked include:
- Data latency (DL)
- Events produced per second (PE)
- Events consumed per second (CE)
- Average time spent in queue (TQ)

## Dependencies and Requirements

- Python 3.8 or higher
- PostgreSQL database
- Broker API access (Alpaca Markets, Gemini)
- Data provider (Alpaca, Polygon.io)
- Optional: TA-Lib for technical analysis
- Optional: Google Cloud Platform for monitoring and tracing

## Quick Start Guide

1. Install LiuAlgoTrader:
   ```bash
   pip install liualgotrader
   ```

2. Run the quickstart wizard:
   ```bash
   liu quickstart
   ```

3. Create a `tradeplan.toml` configuration file defining scanners and strategies

4. Run the trader application:
   ```bash
   trader
   ```

## Code Examples

### Sample Strategy Implementation

```python
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
from liualgotrader.strategies.base import Strategy, StrategyType
from liualgotrader.common.trading_data import (buy_indicators, 
                                             sell_indicators, 
                                             stop_prices,
                                             target_prices)

class MyStrategy(Strategy):
    def __init__(
        self,
        batch_id: str,
        schedule: List[Dict],
        data_loader = None,
        my_param: int = 5,
    ):
        super().__init__(
            name=type(self).__name__,
            type=StrategyType.DAY_TRADING,
            batch_id=batch_id,
            schedule=schedule,
            data_loader=data_loader,
        )
        self.my_param = my_param

    async def run(
        self,
        symbol: str,
        shortable: bool,
        position: float,
        now: datetime,
        minute_history: pd.DataFrame,
        portfolio_value: float = None,
        debug: bool = False,
        backtesting: bool = False,
    ) -> Tuple[bool, Dict]:
        # Implement your trading logic here
        current_price = minute_history.iloc[-1].close
        
        # Buy signal
        if await super().is_buy_time(now) and not position:
            # Set target and stop prices
            target_prices[symbol] = current_price * 1.03
            stop_prices[symbol] = current_price * 0.98
            
            # Store indicators for analysis
            buy_indicators[symbol] = {"reason": "breakout_pattern"}
            
            return True, {
                "side": "buy",
                "qty": "10",
                "type": "limit",
                "limit_price": current_price
            }
            
        # Sell signal
        elif position > 0 and (
            current_price >= target_prices[symbol] or
            current_price <= stop_prices[symbol]
        ):
            sell_indicators[symbol] = {
                "reason": "target_reached" if current_price >= target_prices[symbol]
                else "stop_triggered"
            }
            
            return True, {
                "side": "sell",
                "qty": str(position),
                "type": "market"
            }
            
        return False, {}
```

### Sample Configuration

```toml
[scanners]
    [scanners.momentum]
    min_volume = 30000
    min_gap = 3.5
    min_last_dv = 500000
    max_share_price = 20.0
    min_share_price = 2.0
    from_market_open = 15
    recurrence = 5
    target_strategy_name = "MyStrategy"

[strategies]
    [strategies.MyStrategy]
    filename = "strategies/my_strategy.py"
    my_param = 10
    
    [[strategies.MyStrategy.schedule]]
    start = 15
    duration = 150
``` 