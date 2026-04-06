# Blankly Handlers

## Handler Interfaces and Responsibilities

Blankly organizes its functionality around several key handler types that process different events in the trading system. Each handler interface follows a specific signature and is responsible for different aspects of the trading strategy.

### Price Event Handlers

Price event handlers are the core of most trading strategies, responsible for processing price updates:

```python
def price_event(price, symbol, state):
    """
    Handle price updates for a specific symbol.
    
    Args:
        price (float): The current price of the asset
        symbol (str): The trading symbol (e.g., 'BTC-USD')
        state (StrategyState): The strategy state object
    
    Returns:
        None
    """
    # Trading logic goes here
    pass
```

**Responsibilities:**
- Process new price data
- Update technical indicators
- Make trading decisions
- Execute orders when conditions are met
- Update strategy state based on price changes

**Registration:**
```python
strategy = Strategy(exchange)
strategy.add_price_event(price_event, 'BTC-USD', resolution='1h', init=init)
```

### Initialization Handlers

Initialization handlers set up the initial state for a strategy or data stream:

```python
def init(symbol, state):
    """
    Initialize the strategy for a specific symbol.
    
    Args:
        symbol (str): The trading symbol (e.g., 'BTC-USD')
        state (StrategyState): The strategy state object
    
    Returns:
        None
    """
    # Initialization logic goes here
    pass
```

**Responsibilities:**
- Set up initial strategy variables
- Load historical data for context
- Initialize technical indicators
- Establish initial portfolio allocations
- Set up risk management parameters

**Registration:**
```python
# Provided as an argument to add_price_event
strategy.add_price_event(price_event, 'BTC-USD', resolution='1h', init=init)
```

### Order Event Handlers

Order event handlers process updates to order status:

```python
def order_event(order, state):
    """
    Handle order status updates.
    
    Args:
        order (Order): The order object with status updates
        state (StrategyState): The strategy state object
    
    Returns:
        None
    """
    # Order processing logic goes here
    pass
```

**Responsibilities:**
- Track order lifecycle (created, filled, canceled, rejected)
- Update position tracking after fills
- Implement post-fill logic (e.g., setting stop losses)
- Handle order rejections or failures
- Record trade history

**Registration:**
```python
strategy.add_order_event(order_event)
```

### Scheduled Event Handlers

Scheduled event handlers execute at specified time intervals:

```python
def scheduled_event(state):
    """
    Execute scheduled tasks at specified intervals.
    
    Args:
        state (StrategyState): The strategy state object
    
    Returns:
        None
    """
    # Scheduled task logic goes here
    pass
```

**Responsibilities:**
- Perform periodic portfolio rebalancing
- Run regular risk assessments
- Download external data on schedule
- Generate periodic reports
- Clean up stale orders or state data

**Registration:**
```python
strategy.add_scheduled_event(scheduled_event, '1d')  # Daily execution
```

### Custom Data Handlers

Custom data handlers process non-price data from external sources:

```python
def custom_data_event(data, state):
    """
    Process custom data from external sources.
    
    Args:
        data (dict): The custom data received
        state (StrategyState): The strategy state object
    
    Returns:
        None
    """
    # Custom data processing logic goes here
    pass
```

**Responsibilities:**
- Process alternative data feeds
- Integrate external signals into strategy
- Update state based on non-price information
- Trigger trading decisions based on external events

**Registration:**
Custom data handlers typically need custom implementation with the appropriate data source.

### Websocket Data Handlers

Websocket handlers process real-time data streams from exchanges:

```python
def websocket_message(message, websocket):
    """
    Process raw websocket messages from exchanges.
    
    Args:
        message (dict): The raw message from the websocket
        websocket (WebsocketManager): The websocket manager instance
    
    Returns:
        None
    """
    # Websocket message processing logic goes here
    pass
```

**Responsibilities:**
- Parse raw exchange messages
- Update order books or ticker data
- Forward processed data to appropriate strategy components
- Handle connection maintenance

**Registration:**
```python
# Usually handled internally by Blankly, but can be customized
websocket_manager.add_handler(channel_name, websocket_message)
```

## Input/Output Specifications

Each handler type has specific input and output specifications:

### Price Event Handlers

**Inputs:**
- `price` (float): Current price of the asset
- `symbol` (str): Trading symbol identifier (e.g., 'BTC-USD')
- `state` (StrategyState): Strategy state object containing:
  - `interface`: Exchange interface
  - `variables`: User-defined state dictionary
  - Other strategy context

**Outputs:**
- No direct return value
- Side effects:
  - State modifications via `state.variables`
  - Order execution via `state.interface.market_order()`, etc.
  - Log entries or notifications

**Example:**
```python
def price_event(price, symbol, state):
    # Input validation
    if not isinstance(price, (int, float)) or price <= 0:
        raise ValueError(f"Invalid price: {price}")
    
    # Process price data
    state.variables['last_price'] = price
    state.variables['price_history'].append(price)
    
    # Execute trading logic
    if len(state.variables['price_history']) >= 20:
        sma = sum(state.variables['price_history'][-20:]) / 20
        if price > sma * 1.02 and not state.variables.get('in_position', False):
            # Buy signal
            funds_to_use = state.interface.cash * 0.95  # Use 95% of available cash
            state.interface.market_order(symbol, 'buy', funds=funds_to_use)
            state.variables['in_position'] = True
            state.variables['entry_price'] = price
        elif price < sma * 0.98 and state.variables.get('in_position', False):
            # Sell signal
            base_asset = symbol.split('-')[0]
            available = state.interface.account[base_asset]['available']
            state.interface.market_order(symbol, 'sell', size=available)
            state.variables['in_position'] = False
            
            # Record trade outcome
            profit_pct = (price / state.variables['entry_price'] - 1) * 100
            state.variables['trades'].append({
                'entry': state.variables['entry_price'],
                'exit': price,
                'profit_pct': profit_pct
            })
```

### Initialization Handlers

**Inputs:**
- `symbol` (str): Trading symbol identifier
- `state` (StrategyState): Strategy state object (same as price_event)

**Outputs:**
- No direct return value
- Side effects:
  - Initialization of `state.variables`
  - Initial data loading
  - Setting up indicators

**Example:**
```python
def init(symbol, state):
    # Initialize variables dictionary
    state.variables['in_position'] = False
    state.variables['entry_price'] = 0
    state.variables['trades'] = []
    state.variables['stop_loss_pct'] = 0.05
    state.variables['take_profit_pct'] = 0.1
    
    # Load historical data for context
    history = state.interface.history(symbol, 100, resolution='1d')
    
    # Initialize price history with historical closes
    state.variables['price_history'] = history['close'].tolist()
    
    # Initialize technical indicators
    state.variables['sma'] = sum(state.variables['price_history'][-20:]) / 20
    
    # Log initialization
    print(f"Initialized strategy for {symbol} with {len(history)} historical data points")
```

### Order Event Handlers

**Inputs:**
- `order` (Order): Order object containing:
  - `id`: Unique order identifier
  - `symbol`: Trading symbol
  - `side`: Buy or sell
  - `size`: Order size
  - `type`: Market, limit, etc.
  - `status`: Current status (pending, filled, etc.)
  - `price`: Order price (if applicable)
  - Other order details
- `state` (StrategyState): Strategy state object

**Outputs:**
- No direct return value
- Side effects:
  - Order status tracking
  - Position updates
  - Triggering follow-up actions

**Example:**
```python
def order_event(order, state):
    # Track all orders
    if 'order_history' not in state.variables:
        state.variables['order_history'] = []
    state.variables['order_history'].append({
        'id': order.id,
        'symbol': order.symbol,
        'side': order.side,
        'size': order.size,
        'price': order.price,
        'status': order.status,
        'timestamp': time.time()
    })
    
    # Handle filled orders
    if order.status == 'filled':
        print(f"Order filled: {order.id} for {order.symbol}")
        
        # Handle buy fills - set stop loss and take profit
        if order.side == 'buy':
            # Set stop loss at 5% below purchase price
            stop_price = order.price * (1 - state.variables['stop_loss_pct'])
            state.interface.stop_loss(order.symbol, stop_price, order.size)
            
            # Set take profit at 10% above purchase price
            take_profit_price = order.price * (1 + state.variables['take_profit_pct'])
            state.interface.take_profit(order.symbol, take_profit_price, order.size)
            
            # Update position tracking
            state.variables['in_position'] = True
            state.variables['active_position'] = {
                'entry_price': order.price,
                'size': order.size,
                'entry_time': time.time()
            }
    
    # Handle canceled orders
    elif order.status == 'canceled':
        print(f"Order canceled: {order.id} for {order.symbol}")
        # Implement any logic for canceled orders
    
    # Handle rejected orders
    elif order.status == 'rejected':
        print(f"Order rejected: {order.id} for {order.symbol}")
        # Implement retry logic or alternative actions
```

### Scheduled Event Handlers

**Inputs:**
- `state` (StrategyState): Strategy state object

**Outputs:**
- No direct return value
- Side effects:
  - Periodic state updates
  - Scheduled actions

**Example:**
```python
def scheduled_event(state):
    # Calculate overall portfolio performance
    portfolio_value = state.interface.get_portfolio_value()
    
    if 'portfolio_history' not in state.variables:
        state.variables['portfolio_history'] = []
    
    state.variables['portfolio_history'].append({
        'timestamp': time.time(),
        'value': portfolio_value
    })
    
    # Clean up state - limit history length to avoid memory issues
    if len(state.variables['portfolio_history']) > 1000:
        state.variables['portfolio_history'] = state.variables['portfolio_history'][-1000:]
    
    # Generate periodic report
    if len(state.variables['portfolio_history']) > 1:
        initial_value = state.variables['portfolio_history'][0]['value']
        current_value = state.variables['portfolio_history'][-1]['value']
        performance_pct = (current_value / initial_value - 1) * 100
        print(f"Portfolio performance: {performance_pct:.2f}%")
        
        # Log trade statistics
        if 'trades' in state.variables and state.variables['trades']:
            profitable_trades = sum(1 for t in state.variables['trades'] if t['profit_pct'] > 0)
            total_trades = len(state.variables['trades'])
            win_rate = profitable_trades / total_trades if total_trades > 0 else 0
            print(f"Win rate: {win_rate:.2f} ({profitable_trades}/{total_trades})")
```

## Error Handling Strategies

Blankly implements several error handling strategies to ensure robust operation:

### 1. Exception Handling in User Handlers

Strategy code should implement try-except blocks to catch and handle exceptions:

```python
def price_event(price, symbol, state):
    try:
        # Strategy logic here
        if price > calculate_threshold(state):
            state.interface.market_order(symbol, 'buy', funds=100)
    except Exception as e:
        # Log the error
        print(f"Error in price_event: {str(e)}")
        
        # Update error tracking in state
        if 'errors' not in state.variables:
            state.variables['errors'] = []
        state.variables['errors'].append({
            'timestamp': time.time(),
            'error': str(e),
            'price': price,
            'symbol': symbol
        })
        
        # Optionally implement recovery logic
        if state.variables.get('error_count', 0) < 5:
            state.variables['error_count'] = state.variables.get('error_count', 0) + 1
        else:
            # Too many errors, enter safe mode
            state.variables['safe_mode'] = True
            print("Too many errors, entering safe mode")
```

### 2. Exchange API Error Handling

When interacting with exchange APIs, specific error handling is needed:

```python
def place_order_with_retry(symbol, side, size, state, max_retries=3):
    """Place an order with retry logic for API errors."""
    retries = 0
    while retries < max_retries:
        try:
            # Attempt to place order
            order = state.interface.market_order(symbol, side, size=size)
            return order
        except ConnectionError as e:
            # Connection issue - wait and retry
            retries += 1
            wait_time = 0.5 * (2 ** retries)  # Exponential backoff
            print(f"Connection error, retrying in {wait_time}s: {str(e)}")
            time.sleep(wait_time)
        except RateLimitError as e:
            # Rate limit hit - wait longer
            retries += 1
            wait_time = 1.0 * (2 ** retries)
            print(f"Rate limit error, retrying in {wait_time}s: {str(e)}")
            time.sleep(wait_time)
        except InsufficientFundsError:
            # Not enough funds - fundamental issue, don't retry
            print("Insufficient funds for order")
            return None
        except Exception as e:
            # Unknown error
            print(f"Unknown error placing order: {str(e)}")
            retries += 1
            if retries >= max_retries:
                print("Max retries reached, giving up")
                return None
    
    return None  # Failed after all retries
```

### 3. State Validation

Validate state before critical operations:

```python
def validate_state(state, required_keys):
    """Validate that state contains required keys."""
    missing_keys = [key for key in required_keys if key not in state.variables]
    if missing_keys:
        raise ValueError(f"Missing required state variables: {missing_keys}")

def price_event(price, symbol, state):
    try:
        # Validate state before processing
        validate_state(state, ['price_history', 'position_size', 'risk_per_trade'])
        
        # Process with confidence in state validity
        # ...
    except ValueError as e:
        # Handle validation error
        print(f"State validation error: {str(e)}")
        # Initialize missing state
        for key in ['price_history', 'position_size', 'risk_per_trade']:
            if key not in state.variables:
                state.variables[key] = [] if key == 'price_history' else 0
```

### 4. Defensive Input Validation

Validate inputs to prevent processing invalid data:

```python
def price_event(price, symbol, state):
    # Validate price is reasonable
    if price <= 0 or not isinstance(price, (int, float)):
        print(f"Invalid price received: {price}")
        return
    
    # Validate symbol format
    if not isinstance(symbol, str) or '-' not in symbol:
        print(f"Invalid symbol format: {symbol}")
        return
    
    # Check for extreme price movements (possible data error)
    if 'last_price' in state.variables:
        price_change_pct = abs(price / state.variables['last_price'] - 1) * 100
        if price_change_pct > 20:  # 20% price change threshold
            print(f"Warning: Extreme price change detected: {price_change_pct:.2f}%")
            # Consider additional validation or defensive action
    
    # Now process the validated data
    state.variables['last_price'] = price
    # Continue with normal processing...
```

### 5. Graceful Degradation

Implement fallback mechanisms for partial system failures:

```python
def price_event(price, symbol, state):
    # Check if in degraded mode
    if state.variables.get('degraded_mode', False):
        # Use simplified, more conservative strategy
        simplified_strategy(price, symbol, state)
        return
    
    try:
        # Try to use full-featured strategy
        full_strategy(price, symbol, state)
    except Exception as e:
        print(f"Error in full strategy, switching to degraded mode: {str(e)}")
        state.variables['degraded_mode'] = True
        # Fall back to simplified strategy
        simplified_strategy(price, symbol, state)

def simplified_strategy(price, symbol, state):
    """A simplified, more robust version of the strategy with fewer features."""
    # Implement basic functionality only
    pass
```

### 6. Critical Error Notification

For critical errors, implement notification mechanisms:

```python
def notify_critical_error(error_message, state):
    """Send notification for critical errors."""
    print(f"CRITICAL ERROR: {error_message}")
    
    # If notification settings exist
    if 'notification_email' in state.variables:
        # Code to send email notification
        pass
    
    # Log to permanent storage
    if 'error_log' not in state.variables:
        state.variables['error_log'] = []
    state.variables['error_log'].append({
        'timestamp': time.time(),
        'error': error_message,
        'critical': True
    })

def price_event(price, symbol, state):
    try:
        # Strategy logic
        pass
    except Exception as e:
        if is_critical_error(e):
            notify_critical_error(str(e), state)
```

## Performance Considerations

Blankly handlers should be optimized for performance, especially in high-frequency strategies:

### 1. Efficient Data Structures

Choose appropriate data structures for state variables:

```python
def init(symbol, state):
    # Use collections.deque for price history (efficient append/pop)
    from collections import deque
    state.variables['price_history'] = deque(maxlen=100)  # Auto-limiting size
    
    # Use dictionaries for O(1) lookups
    state.variables['active_orders'] = {}  # order_id -> order_details
    
    # Use sets for membership testing
    state.variables['processed_signals'] = set()
```

### 2. Vectorized Operations

Utilize vectorized operations for calculations:

```python
def price_event(price, symbol, state):
    # Append to history
    state.variables['price_history'].append(price)
    
    # Inefficient way to calculate moving average
    # prices = list(state.variables['price_history'])
    # sma = sum(prices[-20:]) / min(20, len(prices))
    
    # Efficient approach using numpy
    import numpy as np
    prices = np.array(state.variables['price_history'])
    sma = np.mean(prices[-20:])
    
    # More efficient indicator calculations
    if len(prices) >= 50:
        # Calculate multiple indicators at once
        sma20 = np.mean(prices[-20:])
        sma50 = np.mean(prices[-50:])
        std20 = np.std(prices[-20:])
        
        # Use pre-calculated values for decision making
        if sma20 > sma50 and price > sma20 + std20:
            # Buy signal
            pass
```

### 3. Caching Results

Cache calculation results to avoid redundant work:

```python
def calculate_indicators(prices, state):
    """Calculate technical indicators with caching."""
    # Get current time in seconds (granularity control)
    current_time = int(time.time() / 60) * 60  # Round to minute
    
    # Check if we have cached results
    cache_key = f"indicators_{len(prices)}"
    cache_time = state.variables.get(f"{cache_key}_time", 0)
    
    # If cache is recent enough, use it
    if cache_time == current_time and cache_key in state.variables:
        return state.variables[cache_key]
    
    # Calculate indicators
    import numpy as np
    np_prices = np.array(prices)
    results = {
        'sma20': np.mean(np_prices[-20:]) if len(np_prices) >= 20 else None,
        'sma50': np.mean(np_prices[-50:]) if len(np_prices) >= 50 else None,
        'rsi': calculate_rsi(np_prices) if len(np_prices) >= 14 else None,
        # Add more indicators as needed
    }
    
    # Cache results
    state.variables[cache_key] = results
    state.variables[f"{cache_key}_time"] = current_time
    
    return results
```

### 4. Throttling API Calls

Minimize exchange API calls with proper throttling:

```python
def get_account_with_throttling(interface, state):
    """Get account information with throttling to reduce API calls."""
    current_time = time.time()
    last_account_check = state.variables.get('last_account_check', 0)
    
    # Check if we need to refresh (limit to once per minute)
    if current_time - last_account_check > 60:
        account = interface.account
        state.variables['cached_account'] = account
        state.variables['last_account_check'] = current_time
        return account
    else:
        return state.variables.get('cached_account', interface.account)
```

### 5. Resource Management

Clean up resources to prevent memory leaks:

```python
def init(symbol, state):
    # Set up maximum history length
    state.variables['max_history_length'] = 1000
    state.variables['price_history'] = []
    state.variables['order_history'] = []

def price_event(price, symbol, state):
    # Add to history
    state.variables['price_history'].append(price)
    
    # Enforce maximum history length
    max_len = state.variables['max_history_length']
    if len(state.variables['price_history']) > max_len:
        # Trim history to prevent unbounded growth
        state.variables['price_history'] = state.variables['price_history'][-max_len:]
    
    # Periodically clean up order history
    if 'order_history' in state.variables and len(state.variables['order_history']) > max_len:
        # Keep only recent and important orders
        state.variables['order_history'] = state.variables['order_history'][-max_len:]
```

### 6. Profiling and Optimization

Add performance monitoring to identify bottlenecks:

```python
def price_event(price, symbol, state):
    start_time = time.time()
    
    # Track performance of different sections
    timings = {}
    
    # Data preparation
    section_start = time.time()
    state.variables['price_history'].append(price)
    timings['data_prep'] = time.time() - section_start
    
    # Indicator calculation
    section_start = time.time()
    indicators = calculate_indicators(state.variables['price_history'], state)
    timings['indicators'] = time.time() - section_start
    
    # Decision making
    section_start = time.time()
    decision = make_trading_decision(price, indicators, state)
    timings['decision'] = time.time() - section_start
    
    # Order execution
    section_start = time.time()
    if decision['action'] in ['buy', 'sell']:
        execute_order(decision, symbol, state)
    timings['execution'] = time.time() - section_start
    
    # Overall timing
    total_time = time.time() - start_time
    
    # Record performance metrics
    if 'performance_metrics' not in state.variables:
        state.variables['performance_metrics'] = []
    
    # Only keep detailed metrics periodically
    if len(state.variables['performance_metrics']) % 100 == 0:
        state.variables['performance_metrics'].append({
            'timestamp': time.time(),
            'total_time': total_time,
            'detailed': timings
        })
    else:
        state.variables['performance_metrics'].append({
            'timestamp': time.time(),
            'total_time': total_time
        })
    
    # Check for performance issues
    if total_time > 0.1:  # More than 100ms is slow
        print(f"Performance warning: Price event took {total_time*1000:.2f}ms")
        # Identify slow sections
        slow_sections = [k for k, v in timings.items() if v > 0.05]
        if slow_sections:
            print(f"Slow sections: {', '.join(slow_sections)}")
```

## Edge Cases and Their Handling

Blankly handlers need to address various edge cases:

### 1. Market Gaps and Data Discontinuities

Handle missing data points or market gaps:

```python
def price_event(price, symbol, state):
    current_time = time.time()
    last_update_time = state.variables.get('last_update_time', current_time)
    expected_interval = 60  # 1 minute expected interval
    
    # Check for time gap
    time_gap = current_time - last_update_time
    if time_gap > expected_interval * 5:  # Gap of more than 5 intervals
        print(f"Detected data gap of {time_gap:.1f}s ({time_gap/expected_interval:.1f} intervals)")
        
        # Handle the gap
        handle_data_gap(price, symbol, state, time_gap)
    
    # Update last time
    state.variables['last_update_time'] = current_time
    
    # Continue with normal processing
    # ...

def handle_data_gap(price, symbol, state, gap_size):
    """Handle a gap in price data."""
    last_price = state.variables.get('last_price', price)
    
    # Option 1: Fill with last known price
    # for _ in range(int(gap_size / expected_interval)):
    #     state.variables['price_history'].append(last_price)
    
    # Option 2: Linear interpolation
    intervals = int(gap_size / 60)
    if intervals > 1:
        price_diff = price - last_price
        for i in range(1, intervals):
            interpolated_price = last_price + (price_diff * i / intervals)
            state.variables['price_history'].append(interpolated_price)
    
    # Option 3: Get historical data to fill gap
    # try:
    #     # Convert gap to appropriate time period
    #     history = state.interface.history(symbol, to=gap_size, resolution='1m')
    #     # Process the returned data
    # except Exception as e:
    #     print(f"Failed to get history for gap: {str(e)}")
    
    # Flag that a gap was handled
    state.variables['last_gap_handled'] = time.time()
    state.variables['last_gap_size'] = gap_size
```

### 2. Extreme Market Volatility

Handle extreme market conditions:

```python
def price_event(price, symbol, state):
    last_price = state.variables.get('last_price')
    
    if last_price is not None:
        # Calculate price change
        price_change = abs(price / last_price - 1)
        
        # Check for extreme volatility
        if price_change > 0.1:  # 10% price change
            print(f"Extreme volatility detected: {price_change*100:.2f}% change")
            
            # Implement volatility handling strategy
            if state.variables.get('volatility_protection', True):
                # Option 1: Reduce position sizes
                state.variables['position_size_multiplier'] = 0.5  # Half normal size
                
                # Option 2: Widen stop losses
                state.variables['stop_loss_pct'] = state.variables.get('normal_stop_loss_pct', 0.05) * 2
                
                # Option 3: Pause trading temporarily
                state.variables['pause_trading_until'] = time.time() + 3600  # Pause for 1 hour
                
                # Option 4: Switch to a more conservative strategy
                state.variables['use_conservative_strategy'] = True
    
    # Continue processing, possibly with adjusted parameters
    if state.variables.get('pause_trading_until', 0) > time.time():
        print("Trading paused due to extreme volatility")
        return
    
    # Use adjusted parameters if in volatility mode
    position_multiplier = state.variables.get('position_size_multiplier', 1.0)
    
    # Store current price for next comparison
    state.variables['last_price'] = price
```

### 3. Exchange Downtime or Maintenance

Handle exchange unavailability:

```python
def price_event(price, symbol, state):
    try:
        # Attempt to get exchange data
        account = state.interface.account
        
        # If we get here, exchange is available
        if state.variables.get('exchange_down', False):
            print("Exchange connection restored")
            state.variables['exchange_down'] = False
            state.variables['exchange_down_until'] = 0
        
        # Regular trading logic...
    except ConnectionError:
        # Exchange might be down
        handle_exchange_downtime(state)

def handle_exchange_downtime(state):
    current_time = time.time()
    
    # Update downtime tracking
    if not state.variables.get('exchange_down', False):
        # First detection of downtime
        state.variables['exchange_down'] = True
        state.variables['exchange_down_since'] = current_time
        print("Exchange connection lost")
    
    downtime_duration = current_time - state.variables.get('exchange_down_since', current_time)
    
    # Implement graduated response based on downtime duration
    if downtime_duration < 300:  # Less than 5 minutes
        # Just wait, no special action
        state.variables['exchange_down_until'] = current_time + 60  # Check again in 1 minute
    elif downtime_duration < 3600:  # Less than 1 hour
        # Cancel open orders when connection returns
        state.variables['cancel_orders_on_reconnect'] = True
        state.variables['exchange_down_until'] = current_time + 300  # Check again in 5 minutes
    else:  # More than 1 hour
        # Prepare for significant recovery process
        state.variables['major_recovery_needed'] = True
        state.variables['exchange_down_until'] = current_time + 900  # Check again in 15 minutes
```

### 4. Order Size Constraints

Handle exchange-specific order constraints:

```python
def place_valid_order(symbol, side, size, funds, state):
    """Place an order ensuring it meets exchange constraints."""
    # Get minimum order size for this symbol
    min_size = get_min_order_size(symbol, state)
    
    # Check if requested size is too small
    if size is not None and size < min_size:
        print(f"Order size {size} below minimum {min_size} for {symbol}")
        
        # Option 1: Round up to minimum
        size = min_size
        
        # Option 2: Skip the order
        # return None
    
    # Check if using funds instead of size
    if funds is not None:
        # Convert funds to size
        price = state.interface.get_price(symbol)
        calculated_size = funds / price
        
        # Check minimum size
        if calculated_size < min_size:
            print(f"Calculated size {calculated_size} below minimum {min_size} for {symbol}")
            
            # Option 1: Use minimum size
            calculated_size = min_size
            
            # Option 2: Skip the order if too small
            # return None
        
        # Place order with adjusted size
        return state.interface.market_order(symbol, side, size=calculated_size)
    else:
        # Place order with direct size
        return state.interface.market_order(symbol, side, size=size)

def get_min_order_size(symbol, state):
    """Get minimum order size for a symbol with caching."""
    # Check cache first
    cache_key = f"min_order_size_{symbol}"
    if cache_key in state.variables:
        return state.variables[cache_key]
    
    # Hard-coded minimums for common assets
    min_sizes = {
        'BTC-USD': 0.0001,
        'ETH-USD': 0.001,
        'SOL-USD': 0.01,
        # Add more as needed
    }
    
    # Use hard-coded value if available
    if symbol in min_sizes:
        min_size = min_sizes[symbol]
    else:
        # Default value
        min_size = 0.001
    
    # Cache the result
    state.variables[cache_key] = min_size
    return min_size
```

### 5. Insufficient Funds

Handle insufficient funds scenarios:

```python
def execute_trade_with_funds_check(symbol, side, funds_ratio, state):
    """Execute a trade with proper funds checking."""
    try:
        # Get available funds
        if side == 'buy':
            # Buying uses quote currency (USD in BTC-USD)
            available_funds = state.interface.cash
        else:  # sell
            # Selling uses base currency (BTC in BTC-USD)
            base_currency = symbol.split('-')[0]
            if base_currency in state.interface.account:
                available_funds = state.interface.account[base_currency]['available']
                # Convert to equivalent cash value
                price = state.interface.get_price(symbol)
                available_funds *= price
            else:
                available_funds = 0
        
        # Calculate trade size
        funds_to_use = available_funds * funds_ratio
        
        # Reduce slightly to account for fees and price movements
        funds_to_use *= 0.995  # Use 99.5% of calculated amount
        
        # Check if funds are sufficient
        min_trade_value = 10  # Minimum trade value in quote currency
        if funds_to_use < min_trade_value:
            print(f"Insufficient funds: {funds_to_use} < {min_trade_value} minimum")
            
            # Options:
            # 1. Skip the trade
            return None
            
            # 2. Use all available funds if above a threshold
            # if available_funds >= min_trade_value:
            #     funds_to_use = available_funds * 0.995
            # else:
            #     return None
        
        # Execute the trade
        if side == 'buy':
            return state.interface.market_order(symbol, side, funds=funds_to_use)
        else:
            # For sells, use size directly
            base_currency = symbol.split('-')[0]
            size = state.interface.account[base_currency]['available'] * funds_ratio
            return state.interface.market_order(symbol, side, size=size)
            
    except Exception as e:
        print(f"Error executing trade: {str(e)}")
        return None
```

### 6. Handling Delisted Assets

Address delisted or suspended assets:

```python
def price_event(price, symbol, state):
    # Check if symbol is in our watch list for potential delisting
    delisted_symbols = state.variables.get('delisted_symbols', set())
    watch_list = state.variables.get('delisting_watch_list', set())
    
    if symbol in delisted_symbols:
        print(f"Skipping delisted symbol: {symbol}")
        return
    
    # Check for signs of delisting
    try:
        # Attempt to get recent trades
        recent_trades = state.interface.get_product_trades(symbol)
        
        # If we've been watching this symbol, check if it's active again
        if symbol in watch_list and recent_trades:
            print(f"Symbol {symbol} appears active again, removing from watch list")
            watch_list.remove(symbol)
            state.variables['delisting_watch_list'] = watch_list
    except Exception as e:
        error_str = str(e).lower()
        if 'not found' in error_str or 'not available' in error_str or 'delisted' in error_str:
            # Likely delisted
            print(f"Symbol {symbol} appears to be delisted: {error_str}")
            
            # Add to delisted set
            delisted_symbols.add(symbol)
            state.variables['delisted_symbols'] = delisted_symbols
            
            # Close any open positions if possible
            try:
                base_currency = symbol.split('-')[0]
                if base_currency in state.interface.account:
                    size = state.interface.account[base_currency]['available']
                    if size > 0:
                        print(f"Closing position for delisted asset {symbol}")
                        state.interface.market_order(symbol, 'sell', size=size)
            except Exception as close_error:
                print(f"Error closing position for delisted asset: {str(close_error)}")
                
            return
        else:
            # Other error, add to watch list
            if symbol not in watch_list:
                watch_list.add(symbol)
                state.variables['delisting_watch_list'] = watch_list
                print(f"Adding {symbol} to delisting watch list due to error: {error_str}")
    
    # Continue with normal processing for active symbols
    # ...
``` 