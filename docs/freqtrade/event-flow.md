# Freqtrade Event Flow

This document details the event flow and processing sequence in the Freqtrade framework. Understanding this flow is crucial for developing effective trading strategies and properly utilizing the framework's capabilities.

## High-Level Event Flow

```mermaid
sequenceDiagram
    participant User
    participant FTBot as FreqtradeBot
    participant Strategy
    participant Exchange
    participant DataProvider
    participant PairList
    participant Persistence
    
    User->>FTBot: Start bot
    FTBot->>PairList: Initialize pair list
    FTBot->>Exchange: Initialize exchange
    FTBot->>DataProvider: Initialize data provider
    FTBot->>Strategy: Initialize strategy
    FTBot->>Persistence: Load open trades
    
    loop Bot Iteration Loop
        FTBot->>PairList: Get tradable pairs
        FTBot->>DataProvider: Refresh OHLCV data
        FTBot->>Strategy: Call bot_loop_start()
        
        loop For each pair
            FTBot->>Strategy: Call populate_indicators()
            FTBot->>Strategy: Call populate_entry_trend()
            FTBot->>Strategy: Call populate_exit_trend()
        end
        
        FTBot->>Exchange: Update open orders
        
        loop For each open order
            alt Order filled
                FTBot->>Strategy: Call order_filled()
            else Order timed out
                FTBot->>Strategy: Call check_entry_timeout() or check_exit_timeout()
            end
        end
        
        loop For each open trade
            FTBot->>Strategy: Check exit conditions
            alt Exit signal or stop loss
                FTBot->>Strategy: Call confirm_trade_exit()
                FTBot->>Exchange: Execute exit order
            else Position adjustment
                FTBot->>Strategy: Call adjust_trade_position()
                alt Adjustment needed
                    FTBot->>Exchange: Execute adjustment order
                end
            end
        end
        
        alt Trade slots available
            loop For each pair with entry signal
                FTBot->>Strategy: Call confirm_trade_entry()
                FTBot->>Strategy: Call leverage() (for margin/futures)
                FTBot->>Strategy: Call custom_stake_amount()
                FTBot->>Exchange: Execute entry order
            end
        end
        
        FTBot->>Persistence: Save trade state
        Note over FTBot: Sleep until next iteration
    end
```

## Detailed Event Processing Sequence

Freqtrade follows a structured event flow that processes market data, generates signals, and executes trades. The following sections detail this flow.

### 1. Initialization Phase

```mermaid
flowchart TD
    Start[Start Bot] --> LoadConfig[Load Configuration]
    LoadConfig --> InitExchange[Initialize Exchange]
    InitExchange --> InitPairList[Initialize PairList]
    InitPairList --> InitDataProvider[Initialize DataProvider]
    InitDataProvider --> InitStrategy[Initialize Strategy]
    InitStrategy --> LoadTrades[Load Open Trades]
    LoadTrades --> StartMainLoop[Start Main Loop]
    
    InitStrategy --> CallStratInit[Call strategy.init]
    CallStratInit --> LoadIndicators[Load Indicators]
```

During initialization:

1. The bot loads the configuration file and initializes all components
2. The exchange connection is established
3. The pair list manager is initialized with configured pair list providers
4. The data provider is set up to fetch market data
5. The strategy is initialized, calling its `init()` method
6. Open trades are loaded from the database
7. The main bot loop is started

### 2. Main Bot Loop

```mermaid
flowchart TD
    StartLoop[Start Loop Iteration] --> GetPairs[Get Tradable Pairs]
    GetPairs --> FetchData[Fetch OHLCV Data]
    FetchData --> CallBotLoopStart[Call bot_loop_start]
    CallBotLoopStart --> ProcessPairs[Process Pairs]
    ProcessPairs --> ProcessOpenOrders[Process Open Orders]
    ProcessOpenOrders --> ProcessOpenTrades[Process Open Trades]
    ProcessOpenTrades --> ProcessEntrySignals[Process Entry Signals]
    ProcessEntrySignals --> SaveState[Save State]
    SaveState --> Sleep[Sleep Until Next Iteration]
    Sleep --> StartLoop
    
    ProcessPairs --> PopulateIndicators[Call populate_indicators]
    PopulateIndicators --> PopulateEntryTrend[Call populate_entry_trend]
    PopulateEntryTrend --> PopulateExitTrend[Call populate_exit_trend]
```

The main bot loop runs at regular intervals (configurable via `internals.process_throttle_secs`) and performs the following actions:

1. Get the current list of tradable pairs from the pair list manager
2. Fetch OHLCV data for all pairs (only once per candle to minimize API calls)
3. Call the strategy's `bot_loop_start()` callback
4. Process each pair by calling the strategy's populate methods
5. Process open orders (check for fills, timeouts, etc.)
6. Process open trades (check for exit conditions, adjustments, etc.)
7. Process entry signals for new trades
8. Save the current state to the database
9. Sleep until the next iteration

### 3. Order Processing Flow

```mermaid
stateDiagram-v2
    [*] --> Created: Order created
    Created --> Open: Order sent to exchange
    Open --> Filled: Order executed
    Open --> Canceled: Order canceled
    Open --> Expired: Order expired
    Filled --> [*]: Trade updated
    Canceled --> [*]
    Expired --> [*]
    
    state Open {
        [*] --> CheckingStatus
        CheckingStatus --> Timeout: Check timeout
        CheckingStatus --> AdjustPrice: Check price adjustment
        
        Timeout --> [*]: Call timeout callback
        AdjustPrice --> [*]: Call adjust_order_price()
    }
```

Order processing follows these steps:

1. When an order is created, it's added to the list of open orders
2. The order is sent to the exchange
3. During each bot iteration, the status of open orders is checked
4. If an order is filled, the corresponding trade is updated and the `order_filled()` callback is called
5. If an order times out, the appropriate timeout callback is called
6. If price adjustment is enabled, the `adjust_order_price()` callback is called
7. Orders can be canceled manually or by the bot based on certain conditions

### 4. Trade Processing Flow

```mermaid
flowchart TD
    CheckTrades[Check Open Trades] --> LoopTrades[Loop Through Trades]
    LoopTrades --> CheckStoploss[Check Stoploss]
    CheckStoploss --> CheckROI[Check ROI]
    CheckROI --> CheckExitSignal[Check Exit Signal]
    CheckExitSignal --> CheckCustomExit[Call custom_exit]
    
    CheckStoploss --> PrepareExit[Prepare Exit]
    CheckROI --> PrepareExit
    CheckExitSignal --> PrepareExit
    CheckCustomExit --> PrepareExit
    
    PrepareExit --> GetExitPrice[Get Exit Price]
    GetExitPrice --> CallCustomExitPrice[Call custom_exit_price]
    CallCustomExitPrice --> ConfirmExit[Call confirm_trade_exit]
    ConfirmExit --> ExecuteExit[Execute Exit Order]
    
    LoopTrades --> CheckAdjustment[Call adjust_trade_position]
    CheckAdjustment --> ExecuteAdjustment[Execute Adjustment Order]
```

Trade processing includes:

1. Checking each open trade for exit conditions
2. Evaluating stop-loss conditions (including trailing stop-loss)
3. Checking ROI (Return on Investment) thresholds
4. Looking for exit signals from the strategy
5. Calling the `custom_exit()` callback for custom exit logic
6. If an exit is triggered, determining the exit price
7. Calling `confirm_trade_exit()` to confirm the exit
8. Executing the exit order if confirmed
9. Checking for position adjustments via `adjust_trade_position()`
10. Executing adjustment orders if needed

### 5. Entry Signal Processing

```mermaid
flowchart TD
    CheckEntries[Check Entry Signals] --> CheckSlots[Check Available Trade Slots]
    CheckSlots --> LoopPairs[Loop Through Pairs]
    LoopPairs --> GetEntryPrice[Get Entry Price]
    GetEntryPrice --> CallCustomEntryPrice[Call custom_entry_price]
    CallCustomEntryPrice --> GetLeverage[Call leverage]
    GetLeverage --> GetStakeAmount[Call custom_stake_amount]
    GetStakeAmount --> ConfirmEntry[Call confirm_trade_entry]
    ConfirmEntry --> ExecuteEntry[Execute Entry Order]
```

Entry signal processing includes:

1. Checking if trade slots are available (based on `max_open_trades`)
2. Looping through pairs with entry signals
3. Determining the entry price (based on configuration or `custom_entry_price()`)
4. Calling `leverage()` to determine leverage for margin/futures trading
5. Determining the stake amount via `custom_stake_amount()`
6. Calling `confirm_trade_entry()` to confirm the entry
7. Executing the entry order if confirmed

### 6. Backtesting Event Flow

```mermaid
sequenceDiagram
    participant User
    participant Backtesting
    participant Strategy
    participant DataProvider
    
    User->>Backtesting: Start backtesting
    Backtesting->>DataProvider: Load historical data
    Backtesting->>Strategy: Call bot_start()
    
    loop For each pair
        Backtesting->>Strategy: Call populate_indicators()
        Backtesting->>Strategy: Call populate_entry_trend()
        Backtesting->>Strategy: Call populate_exit_trend()
    end
    
    loop For each candle
        Backtesting->>Strategy: Call bot_loop_start()
        
        loop For each open order
            alt Order timeout
                Backtesting->>Strategy: Call check_entry_timeout() or check_exit_timeout()
            else Order price adjustment
                Backtesting->>Strategy: Call adjust_order_price()
            end
        end
        
        loop For each pair with entry signal
            Backtesting->>Strategy: Call confirm_trade_entry()
            Backtesting->>Strategy: Call leverage()
            Backtesting->>Strategy: Call custom_stake_amount()
            Backtesting->>Strategy: Call order_filled() for entry
        end
        
        loop For each open trade
            Backtesting->>Strategy: Check exit conditions
            alt Exit triggered
                Backtesting->>Strategy: Call confirm_trade_exit()
                Backtesting->>Strategy: Call custom_exit_price()
                Backtesting->>Strategy: Call order_filled() for exit
            else Position adjustment
                Backtesting->>Strategy: Call adjust_trade_position()
                alt Adjustment needed
                    Backtesting->>Strategy: Call order_filled() for adjustment
                end
            end
        end
    end
    
    Backtesting->>User: Return results
```

The backtesting event flow simulates the live trading process:

1. Historical data is loaded for all pairs
2. The strategy's `bot_start()` callback is called once
3. Indicators and signals are calculated for all pairs
4. The simulation processes each candle sequentially
5. For each candle, the same callbacks as in live trading are called
6. Orders are simulated based on the candle's price range
7. Trades are tracked and performance metrics are calculated
8. Results are returned to the user

## Event Timing Considerations

Understanding the timing of events in Freqtrade is crucial for accurate strategy development:

1. **Candle Processing**: By default, Freqtrade processes candles after they are completed. This means that when processing a 5-minute candle at 10:05, you're working with data from 10:00-10:05.

2. **Order Execution**: In live trading, orders are executed asynchronously. In backtesting, orders are simulated based on the price range of the candle.

3. **Callback Frequency**: In live trading, callbacks like `bot_loop_start()` are called on each iteration (typically every few seconds). In backtesting, they are called once per candle.

4. **Data Availability**: In live trading, only data up to the current moment is available. In backtesting, the strategy has access to all historical data, but the framework prevents look-ahead bias.

## Error Handling in the Event Flow

Freqtrade implements several error handling mechanisms:

1. **Exchange Communication Errors**: Temporary errors are retried with exponential backoff
2. **Order Placement Errors**: Failed orders are logged and can trigger callbacks
3. **Strategy Errors**: Exceptions in strategy code are caught and logged
4. **Data Gaps**: The framework can handle missing candles in historical data

## Example Event Flow

Here's a concrete example of the event flow for a simple moving average crossover strategy:

```mermaid
sequenceDiagram
    participant FTBot as FreqtradeBot
    participant SMAStrategy as SMA Crossover Strategy
    participant Exchange
    participant DataProvider
    
    FTBot->>DataProvider: Get OHLCV data for BTC/USDT
    DataProvider->>FTBot: Return OHLCV data
    FTBot->>SMAStrategy: Call populate_indicators()
    SMAStrategy->>SMAStrategy: Calculate SMA(50) and SMA(200)
    FTBot->>SMAStrategy: Call populate_entry_trend()
    SMAStrategy->>SMAStrategy: Check if SMA(50) crosses above SMA(200)
    SMAStrategy->>FTBot: Return entry signals
    FTBot->>SMAStrategy: Call populate_exit_trend()
    SMAStrategy->>SMAStrategy: Check if SMA(50) crosses below SMA(200)
    SMAStrategy->>FTBot: Return exit signals
    
    alt Entry signal detected
        FTBot->>SMAStrategy: Call confirm_trade_entry()
        SMAStrategy->>FTBot: Confirm entry
        FTBot->>SMAStrategy: Call custom_stake_amount()
        SMAStrategy->>FTBot: Return stake amount
        FTBot->>Exchange: Place buy order
        Exchange->>FTBot: Order placed
        
        alt Order filled
            Exchange->>FTBot: Order filled notification
            FTBot->>SMAStrategy: Call order_filled()
            FTBot->>Persistence: Save trade
        end
    end
    
    alt Exit signal for open trade
        FTBot->>SMAStrategy: Call confirm_trade_exit()
        SMAStrategy->>FTBot: Confirm exit
        FTBot->>Exchange: Place sell order
        Exchange->>FTBot: Order placed
        
        alt Order filled
            Exchange->>FTBot: Order filled notification
            FTBot->>SMAStrategy: Call order_filled()
            FTBot->>Persistence: Update trade as closed
        end
    end
```

This example demonstrates how a simple strategy interacts with the Freqtrade event flow to generate and process trading signals.
