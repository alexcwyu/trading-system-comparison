# TensorTrade Event Flow

This document details the event flow and processing sequence in the TensorTrade framework. Understanding this flow is crucial for developing effective trading strategies and properly utilizing the framework's reinforcement learning capabilities.

## High-Level Event Flow

```mermaid
sequenceDiagram
    participant Agent
    participant TradingEnv
    participant ActionScheme
    participant RewardScheme
    participant Observer
    participant Portfolio
    participant Exchange
    
    Agent->>TradingEnv: reset()
    TradingEnv->>Portfolio: reset()
    TradingEnv->>ActionScheme: reset()
    TradingEnv->>RewardScheme: reset()
    TradingEnv->>Observer: reset()
    TradingEnv->>Observer: observe()
    Observer->>TradingEnv: observation
    TradingEnv->>Agent: initial observation
    
    loop For each step
        Agent->>TradingEnv: step(action)
        TradingEnv->>ActionScheme: get_action(action)
        ActionScheme->>Portfolio: execute(order)
        Portfolio->>Exchange: execute(order)
        Exchange->>Portfolio: update balances
        TradingEnv->>RewardScheme: get_reward(portfolio)
        TradingEnv->>Observer: observe()
        Observer->>TradingEnv: observation
        TradingEnv->>Agent: observation, reward, done, info
    end
```

## Detailed Event Processing Sequence

TensorTrade follows a reinforcement learning paradigm where an agent interacts with a trading environment to learn optimal trading strategies. The following sections detail this flow.

### 1. Initialization Phase

```mermaid
flowchart TD
    Start[Start] --> CreateEnv[Create TradingEnv]
    CreateEnv --> InitComponents[Initialize Components]
    InitComponents --> CreateAgent[Create Agent]
    CreateAgent --> ResetEnv[Reset Environment]
    ResetEnv --> InitialObservation[Get Initial Observation]
    InitialObservation --> ReadyForTraining[Ready for Training]
    
    subgraph "Component Initialization"
        InitComponents --> InitActionScheme[Initialize ActionScheme]
        InitComponents --> InitRewardScheme[Initialize RewardScheme]
        InitComponents --> InitObserver[Initialize Observer]
        InitComponents --> InitStopper[Initialize Stopper]
        InitComponents --> InitInformer[Initialize Informer]
        InitComponents --> InitRenderer[Initialize Renderer]
        InitComponents --> InitPortfolio[Initialize Portfolio]
        InitComponents --> InitExchange[Initialize Exchange]
        InitComponents --> InitDataFeed[Initialize DataFeed]
    end
```

During initialization:

1. The `TradingEnv` is created with all necessary components
2. Each component is initialized with its configuration parameters
3. The reinforcement learning agent is created and connected to the environment
4. The environment is reset to its initial state
5. The initial observation is generated and provided to the agent

### 2. Training Loop

```mermaid
flowchart TD
    Start[Start Training] --> ResetEnv[Reset Environment]
    ResetEnv --> InitialObs[Get Initial Observation]
    InitialObs --> TrainingLoop[Enter Training Loop]
    
    subgraph "Episode Loop"
        TrainingLoop --> SelectAction[Agent Selects Action]
        SelectAction --> ExecuteAction[Execute Action]
        ExecuteAction --> GetReward[Calculate Reward]
        GetReward --> GetNextObs[Get Next Observation]
        GetNextObs --> CheckDone{Episode Done?}
        CheckDone -->|No| SelectAction
        CheckDone -->|Yes| EndEpisode[End Episode]
    end
    
    EndEpisode --> CheckTrainingDone{Training Complete?}
    CheckTrainingDone -->|No| ResetEnv
    CheckTrainingDone -->|Yes| EndTraining[End Training]
```

The training loop follows these steps:

1. Reset the environment to start a new episode
2. Get the initial observation
3. For each step in the episode:
   - The agent selects an action based on the current observation
   - The action is executed in the environment
   - A reward is calculated based on the outcome of the action
   - The next observation is generated
   - The agent updates its policy based on the experience (observation, action, reward, next observation)
4. When the episode ends (either by reaching a terminal state or maximum steps), a new episode begins
5. Training continues until a specified number of episodes or a performance threshold is reached

### 3. Action Execution Flow

```mermaid
flowchart TD
    AgentAction[Agent Action] --> ActionScheme[ActionScheme.get_action]
    ActionScheme --> CreateOrder[Create Order]
    CreateOrder --> ValidateOrder[Validate Order]
    ValidateOrder --> ExecuteOrder[Execute Order]
    
    subgraph "Order Execution"
        ExecuteOrder --> CheckOrderType{Order Type}
        CheckOrderType -->|Market| ExecuteMarket[Execute at Current Price]
        CheckOrderType -->|Limit| CheckLimitCondition{Price Condition Met?}
        CheckLimitCondition -->|Yes| ExecuteLimit[Execute at Limit Price]
        CheckLimitCondition -->|No| HoldOrder[Hold Order]
        CheckOrderType -->|Stop| CheckStopCondition{Price Condition Met?}
        CheckStopCondition -->|Yes| ExecuteStop[Execute at Market Price]
        CheckStopCondition -->|No| HoldOrder
    end
    
    ExecuteMarket --> UpdatePortfolio[Update Portfolio]
    ExecuteLimit --> UpdatePortfolio
    ExecuteStop --> UpdatePortfolio
    HoldOrder --> ReturnState[Return Current State]
    UpdatePortfolio --> ReturnState
```

Action execution follows these steps:

1. The agent selects an action (which could be a discrete index or continuous values)
2. The `ActionScheme` interprets this action and creates the corresponding order(s)
3. The order is validated to ensure it can be executed (e.g., sufficient funds)
4. The order is executed based on its type:
   - Market orders are executed immediately at the current price
   - Limit orders are executed if the price condition is met
   - Stop orders are executed if the stop price is reached
5. The portfolio is updated to reflect the changes in balances
6. The current state is returned to the environment

### 4. Reward Calculation Flow

```mermaid
flowchart TD
    ActionExecuted[Action Executed] --> RewardScheme[RewardScheme.get_reward]
    
    subgraph "Reward Calculation Methods"
        RewardScheme --> SimpleProfit[SimpleProfit]
        RewardScheme --> RiskAdjusted[RiskAdjustedReturns]
        RewardScheme --> PBR[PositionBasedReturn]
        RewardScheme --> ScaledReturns[ScaledReturns]
        
        SimpleProfit --> CalculateNetWorth[Calculate Net Worth Change]
        RiskAdjusted --> CalculateSharpe[Calculate Sharpe Ratio]
        PBR --> CalculateUnrealizedReturn[Calculate Unrealized Return]
        ScaledReturns --> ScaleReward[Scale Reward Value]
    end
    
    CalculateNetWorth --> ReturnReward[Return Reward]
    CalculateSharpe --> ReturnReward
    CalculateUnrealizedReturn --> ReturnReward
    ScaleReward --> ReturnReward
```

Reward calculation follows these steps:

1. After an action is executed, the `RewardScheme` calculates the reward
2. Different reward schemes use different methods:
   - `SimpleProfit`: Calculates the change in net worth
   - `RiskAdjustedReturns`: Uses risk-adjusted metrics like Sharpe ratio
   - `PBR (Position-Based Return)`: Considers both unrealized and realized returns
   - `ScaledReturns`: Scales returns to a more suitable range for learning
3. The calculated reward is returned to the environment and passed to the agent

### 5. Observation Generation Flow

```mermaid
flowchart TD
    StateUpdated[State Updated] --> Observer[Observer.observe]
    
    subgraph "Observation Generation"
        Observer --> GetMarketData[Get Market Data]
        Observer --> GetPortfolioState[Get Portfolio State]
        Observer --> ApplyWindowSize[Apply Window Size]
        
        GetMarketData --> CombineData[Combine Data]
        GetPortfolioState --> CombineData
        ApplyWindowSize --> NormalizeData[Normalize Data]
    end
    
    NormalizeData --> ReturnObservation[Return Observation]
```

Observation generation follows these steps:

1. After the state is updated, the `Observer` generates a new observation
2. The observation typically includes:
   - Market data (prices, volumes, etc.)
   - Portfolio state (balances, positions, etc.)
   - Technical indicators or other features
3. The data is processed according to the window size (historical context)
4. The data is normalized to facilitate learning
5. The observation is returned to the environment and passed to the agent

### 6. Episode Termination Flow

```mermaid
flowchart TD
    AfterStep[After Step] --> Stopper[Stopper.stop]
    
    subgraph "Termination Conditions"
        Stopper --> MaxSteps[Max Steps Reached]
        Stopper --> MaxLoss[Max Loss Exceeded]
        Stopper --> TargetReturn[Target Return Achieved]
        Stopper --> TimeLimit[Time Limit Reached]
        
        MaxSteps --> CheckCondition{Any Condition Met?}
        MaxLoss --> CheckCondition
        TargetReturn --> CheckCondition
        TimeLimit --> CheckCondition
    end
    
    CheckCondition -->|Yes| TerminateEpisode[Terminate Episode]
    CheckCondition -->|No| ContinueEpisode[Continue Episode]
```

Episode termination follows these steps:

1. After each step, the `Stopper` checks if the episode should end
2. Termination conditions can include:
   - Maximum number of steps reached
   - Maximum loss exceeded
   - Target return achieved
   - Time limit reached
3. If any termination condition is met, the episode ends
4. Otherwise, the episode continues

## Event Timing Considerations

Understanding the timing of events in TensorTrade is crucial for accurate strategy development:

1. **Data Synchronization**: All data streams in a `DataFeed` are synchronized to ensure consistent timing across different sources.

2. **Action Execution**: Actions are executed based on the current state of the environment, which includes the latest market data and portfolio state.

3. **Reward Calculation**: Rewards are calculated after actions are executed, based on the resulting state of the portfolio.

4. **Observation Generation**: Observations are generated after the state is updated, providing the agent with the latest information.

5. **Episode Termination**: Episode termination is checked after each step, based on the current state of the environment.

## Error Handling in the Event Flow

TensorTrade implements several error handling mechanisms:

1. **Order Validation**: Orders are validated before execution to ensure they can be executed (e.g., sufficient funds).

2. **Action Clipping**: Actions from the agent can be clipped to ensure they are within valid ranges.

3. **Exception Handling**: Exceptions during execution are caught and handled to prevent the environment from crashing.

4. **Logging**: Detailed logging is available to help diagnose issues during execution.

## Example Event Flow

Here's a concrete example of the event flow for a simple reinforcement learning trading strategy:

```mermaid
sequenceDiagram
    participant Agent as DQN Agent
    participant Env as TradingEnv
    participant Action as BSH ActionScheme
    participant Reward as SimpleProfit RewardScheme
    participant Portfolio
    participant Exchange
    
    Agent->>Env: reset()
    Env->>Portfolio: reset()
    Env->>Agent: initial observation
    
    loop For each step
        Agent->>Env: step(action=1) # Buy action
        Env->>Action: get_action(action=1)
        Action->>Action: Create buy order
        Action->>Portfolio: execute(buy_order)
        Portfolio->>Exchange: execute(buy_order)
        Exchange->>Portfolio: Update balances
        
        Env->>Reward: get_reward(portfolio)
        Reward->>Reward: Calculate net worth change
        Reward->>Env: reward = 0.05
        
        Env->>Env: Generate next observation
        Env->>Agent: observation, reward=0.05, done=False, info={}
        
        Agent->>Env: step(action=2) # Sell action
        Env->>Action: get_action(action=2)
        Action->>Action: Create sell order
        Action->>Portfolio: execute(sell_order)
        Portfolio->>Exchange: execute(sell_order)
        Exchange->>Portfolio: Update balances
        
        Env->>Reward: get_reward(portfolio)
        Reward->>Reward: Calculate net worth change
        Reward->>Env: reward = -0.02
        
        Env->>Env: Generate next observation
        Env->>Agent: observation, reward=-0.02, done=False, info={}
        
        Agent->>Env: step(action=0) # Hold action
        Env->>Action: get_action(action=0)
        Action->>Env: No order to execute
        
        Env->>Reward: get_reward(portfolio)
        Reward->>Reward: Calculate net worth change
        Reward->>Env: reward = 0.01
        
        Env->>Env: Generate next observation
        Env->>Env: Check if episode is done
        Env->>Agent: observation, reward=0.01, done=True, info={}
    end
```

This example demonstrates how a DQN agent interacts with a TensorTrade environment using a simple Buy-Sell-Hold action scheme and a SimpleProfit reward scheme. The agent makes decisions based on the observations it receives, and the environment executes these actions and provides rewards based on the outcomes.
