# LiuAlgoTrader Event Flow

## Event Flow Overview

LiuAlgoTrader uses a producer-consumer architecture with queue-based message passing for event processing. This document details the event types, their flow through the system, and how they are processed.

```mermaid
graph LR
    subgraph "External Sources"
        DP[Data Providers] -->|"WebSocket Updates"| PR
        SC[Scanners] -->|"Symbol Discovery"| PR
    end
    
    subgraph "Producer Process"
        PR[Producer]
        QM[Queue Mapper]
    end
    
    subgraph "Consumer Processes"
        C1[Consumer 1]
        C2[Consumer 2]
        C3[Consumer n]
    end
    
    PR -->|"Symbol Events"| QM
    QM -->|"Symbol A Events"| C1
    QM -->|"Symbol B Events"| C2
    QM -->|"Symbol C Events"| C3
    
    C1 -->|"Execute Strategy"| S1[Strategy Execution]
    C2 -->|"Execute Strategy"| S2[Strategy Execution]
    C3 -->|"Execute Strategy"| S3[Strategy Execution]
    
    S1 -->|"Order"| T1[Trade Execution]
    S2 -->|"Order"| T2[Trade Execution]
    S3 -->|"Order"| T3[Trade Execution]
</graph>
```

## Event Types

LiuAlgoTrader processes several types of events:

1. **Scanner Events**: Events generated when scanners identify new symbols that meet criteria
2. **WebSocket Events**: Data from external providers via WebSockets, including:
   - Second Aggregates (`SEC_AGG`): Price updates aggregated per second
   - Minute Aggregates (`MIN_AGG`): Price updates aggregated per minute 
   - Trade Events (`TRADE`): Individual trade execution events
   - Quote Events (`QUOTE`): Bid/ask quote updates

3. **Strategy Events**: Events generated when strategies make trading decisions
4. **Order Events**: Events related to order placement, fills, and cancellations

## Initialization Phase

```mermaid
sequenceDiagram
    participant T as Trader Application
    participant SC as Scanner Process
    participant PR as Producer Process
    participant C as Consumer Processes
    participant S as Strategies
    participant DB as Database
    
    T->>SC: Start scanner process
    T->>PR: Start producer process
    T->>C: Start consumer processes
    C->>S: Initialize strategies
    SC->>PR: Send initial symbols
    PR->>PR: Map symbols to consumer queues
    PR->>+DB: Record trending symbols
    PR->>PR: Subscribe to data for symbols
</sequence>
```

1. The trader application starts the scanner, producer, and consumer processes
2. Scanners run according to the configuration and identify initial symbols
3. The producer receives these symbols and maps them to consumer queues
4. The producer subscribes to data feeds for these symbols
5. Consumers initialize strategies and prepare to process events

## Normal Operation Event Flow

```mermaid
sequenceDiagram
    participant DP as Data Provider
    participant PR as Producer
    participant QM as Queue Mapper
    participant CQ as Consumer Queue
    participant C as Consumer
    participant S as Strategy
    participant T as Trader
    participant DB as Database
    
    DP->>PR: WebSocket event
    PR->>PR: Pre-process event
    PR->>QM: Route event by symbol
    QM->>CQ: Push to appropriate queue
    CQ->>C: Dequeue event
    C->>C: Process & aggregate data
    C->>S: Call strategy.run()
    S->>S: Make trading decision
    S->>C: Return decision (True/False, action)
    
    alt Trading Decision = True
        C->>T: Submit order
        T->>DB: Record trade intent
        T->>DP: Place order
        DP-->>T: Order acknowledgment
        T-->>C: Update order status
        C-->>S: Call buy/sell callback
        C->>DB: Update trade record
    end
</sequence>
```

During normal operation:

1. The data provider sends events via WebSocket to the producer
2. The producer pre-processes events and determines the target consumer queue
3. The event is pushed to the appropriate consumer queue based on symbol
4. The consumer dequeues the event, processes it, and updates aggregated data
5. The consumer calls the strategy's `run()` method with the latest data
6. If the strategy returns a trading decision, the consumer submits an order
7. The trader component places the order with the broker
8. Order status updates are processed and callbacks triggered

## Periodic Scanner Event Flow

```mermaid
sequenceDiagram
    participant SC as Scanner Process
    participant PR as Producer Process
    participant C as Consumer Process
    
    loop At configured intervals
        SC->>SC: Run scanner
        SC->>PR: New symbols discovered
        PR->>PR: Map symbols to queues
        PR->>PR: Subscribe to data feeds
        PR->>C: New symbols available notification
    end
</sequence>
```

Scanners run periodically according to their configuration:

1. The scanner process runs scanners at configured intervals
2. Newly discovered symbols are sent to the producer
3. The producer maps these symbols to consumer queues
4. The producer subscribes to data feeds for the new symbols

## Error Handling Flow

```mermaid
sequenceDiagram
    participant PR as Producer
    participant C as Consumer
    participant S as Strategy
    
    alt Data Latency Too High
        PR->>PR: Detect high latency
        PR->>PR: Clear backlog
        PR->>C: Send prioritized events
    end
    
    alt Consumer Process Exception
        C->>C: Catch exception
        C->>C: Log error
        C->>C: Continue processing other symbols
    end
    
    alt Strategy Exception
        S->>S: Exception occurs
        C->>C: Catch exception
        C->>C: Log error details
        C->>C: Skip strategy for this event
    end
    
    alt Order Execution Failure
        C->>C: Detect order failure
        C->>C: Log error
        C->>C: Cancel pending order if needed
        C->>S: Notify strategy (optional)
    end
</sequence>
```

LiuAlgoTrader implements robust error handling:

1. **Data Latency Issues**: If data latency exceeds thresholds, the system clears backlogs
2. **Consumer Process Exceptions**: Exceptions in a consumer process are isolated to that process
3. **Strategy Exceptions**: Exceptions in a strategy are isolated to that strategy
4. **Order Execution Failures**: Failed orders are logged and can be handled by the strategy

## End of Day Flow

```mermaid
sequenceDiagram
    participant T as Trader Application
    participant C as Consumer Processes
    participant S as Strategies
    participant DB as Database
    
    alt Day Trading Mode
        T->>C: Market closing soon notification
        C->>S: Liquidation time check
        S->>C: Liquidation orders
        C->>DB: Record liquidation trades
    end
    
    T->>C: Terminate consumer processes
    T->>T: Run end-of-day analysis
    T->>DB: Store gain/loss calculations
    T->>DB: Store trade analysis
</sequence>
```

At the end of the trading day:

1. For day trading strategies, positions are automatically liquidated
2. Consumer processes are terminated
3. End-of-day analysis is performed
4. Results are stored in the database for later review

## Key Performance Considerations

LiuAlgoTrader's event flow is designed for high throughput:

1. **Queue Optimization**: Events are routed to minimize queue contention
2. **Data Latency Monitoring**: The system tracks and manages data latency
3. **Overload Protection**: If a consumer falls behind, it can discard old events
4. **Isolated Processes**: Problems in one consumer don't affect others
5. **Load Balancing**: Symbols are distributed evenly across consumers 