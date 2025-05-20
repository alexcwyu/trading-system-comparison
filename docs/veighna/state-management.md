# VeighNa State Management

## State Model Overview

VeighNa implements a comprehensive state management system that maintains the current state of orders, trades, positions, accounts, and other critical components. The state model is designed to be consistent, accessible, and persistent.

![VeighNa State Management](./images/veighna-state-management.png)

## Core State Components

### MainEngine State

The `MainEngine` is the central component that maintains the global state of the trading system:

```python
class MainEngine:
    """
    Main engine for managing all components.
    """
    
    def __init__(self, event_engine: EventEngine = None):
        """
        Initialize main engine.
        """
        self.event_engine = event_engine or EventEngine()
        self.gateway_dict = {}
        self.app_dict = {}
        self.engine_dict = {}
        
        # Global state
        self.contracts = {}
        self.accounts = {}
        self.positions = {}
        self.orders = {}
        self.trades = {}
        self.quotes = {}
        
        # Register event handlers
        self.event_engine.register(EVENT_CONTRACT, self._process_contract_event)
        self.event_engine.register(EVENT_ACCOUNT, self._process_account_event)
        self.event_engine.register(EVENT_POSITION, self._process_position_event)
        self.event_engine.register(EVENT_ORDER, self._process_order_event)
        self.event_engine.register(EVENT_TRADE, self._process_trade_event)
        self.event_engine.register(EVENT_QUOTE, self._process_quote_event)
```

### Contract State

Contracts represent tradable instruments:

```python
class ContractData(BaseData):
    """
    Contract data.
    """
    
    symbol: str
    exchange: Exchange
    name: str
    product: Product
    size: float
    pricetick: float
    
    min_volume: float = 1
    stop_supported: bool = False
    net_position: bool = False
    history_data: bool = False
    
    option_strike: float = 0
    option_underlying: str = ""
    option_type: OptionType = None
    option_expiry: datetime = None
    
    create_date: str = ""
    open_date: str = ""
    expire_date: str = ""
    
    # For calculating position value
    price_multiplier: int = 1
    
    # Custom contract data
    custom_data = None
```

### Order State

Orders represent trading instructions:

```python
class OrderData(BaseData):
    """
    Order data.
    """
    
    symbol: str
    exchange: Exchange
    orderid: str
    
    type: OrderType = OrderType.LIMIT
    direction: Direction = None
    offset: Offset = Offset.NONE
    price: float = 0
    volume: float = 0
    traded: float = 0
    status: Status = Status.SUBMITTING
    datetime: datetime = None
    reference: str = ""
```

### Trade State

Trades represent executed orders:

```python
class TradeData(BaseData):
    """
    Trade data.
    """
    
    symbol: str
    exchange: Exchange
    orderid: str
    tradeid: str
    
    direction: Direction = None
    offset: Offset = Offset.NONE
    price: float = 0
    volume: float = 0
    datetime: datetime = None
```

### Position State

Positions represent current holdings:

```python
class PositionData(BaseData):
    """
    Position data.
    """
    
    symbol: str
    exchange: Exchange
    direction: Direction
    
    volume: float = 0
    frozen: float = 0
    price: float = 0
    pnl: float = 0
    yd_volume: float = 0
```

### Account State

Accounts represent trading accounts:

```python
class AccountData(BaseData):
    """
    Account data.
    """
    
    accountid: str
    
    balance: float = 0
    frozen: float = 0
    
    # For futures account
    available: float = 0
    commission: float = 0
    margin: float = 0
    close_profit: float = 0
    position_profit: float = 0
```

## State Transitions and Triggers

### Order State Transitions

Orders go through a well-defined lifecycle represented by the `Status` enum:

```python
class Status(Enum):
    """
    Order status.
    """
    SUBMITTING = "提交中"
    NOTTRADED = "未成交"
    PARTTRADED = "部分成交"
    ALLTRADED = "全部成交"
    CANCELLED = "已撤销"
    REJECTED = "拒单"
```

Transitions between these states are triggered by order events:
- `SUBMITTING` → `NOTTRADED`: Order is accepted by the exchange
- `NOTTRADED` → `PARTTRADED`: Order is partially filled
- `PARTTRADED` → `ALLTRADED`: Order is completely filled
- `NOTTRADED` → `CANCELLED`: Order is canceled
- `PARTTRADED` → `CANCELLED`: Partially filled order is canceled
- `SUBMITTING` → `REJECTED`: Order is rejected by the exchange

### Position State Transitions

Position state changes are triggered by trade events:
- New trade in a direction with no existing position: Position is created
- Trade in the same direction as an existing position: Position size increases
- Trade in the opposite direction of an existing position: Position size decreases
- Trade that completely offsets an existing position: Position is closed

## Persistence Mechanisms

VeighNa provides several mechanisms for persisting state:

1. **Database Storage**: State can be stored in a database (SQLite, MySQL)
2. **JSON Files**: State can be saved to JSON files
3. **CSV Export**: State can be exported to CSV files
4. **Custom Storage**: Custom storage backends can be implemented

### Database Storage

VeighNa uses SQLAlchemy for database storage:

```python
class DbEngine:
    """
    Database engine for data storage.
    """
    
    def __init__(self, driver: str = "sqlite", settings: dict = None):
        """
        Initialize database engine.
        """
        self.driver = driver
        self.settings = settings or {}
        
        self.engine = create_engine(self._get_connection_string())
        Base.metadata.create_all(self.engine)
        
        self.session_factory = sessionmaker(bind=self.engine)
        self.session = None
    
    def _get_connection_string(self) -> str:
        """
        Get database connection string.
        """
        if self.driver == "sqlite":
            database = self.settings.get("database", "database.db")
            return f"sqlite:///{database}"
        elif self.driver == "mysql":
            user = self.settings.get("user", "root")
            password = self.settings.get("password", "")
            host = self.settings.get("host", "localhost")
            port = self.settings.get("port", 3306)
            database = self.settings.get("database", "vnpy")
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported driver: {self.driver}")
    
    def save_bar_data(self, bars: List[BarData]):
        """
        Save bar data to database.
        """
        with self.session_factory() as session:
            for bar in bars:
                db_bar = DbBarData(
                    symbol=bar.symbol,
                    exchange=bar.exchange.value,
                    datetime=bar.datetime,
                    interval=bar.interval.value,
                    volume=bar.volume,
                    open_price=bar.open_price,
                    high_price=bar.high_price,
                    low_price=bar.low_price,
                    close_price=bar.close_price,
                )
                session.merge(db_bar)
            session.commit()
    
    # Other methods for saving and loading data...
```

### JSON File Storage

State can also be saved to JSON files:

```python
def save_json(filename: str, data: dict):
    """
    Save data to JSON file.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_json(filename: str) -> dict:
    """
    Load data from JSON file.
    """
    with open(filename, "r") as f:
        return json.load(f)
```

## Recovery Procedures

VeighNa implements several recovery procedures:

1. **Database Recovery**: Restore state from database
2. **File Recovery**: Restore state from files
3. **Exchange Reconciliation**: Reconcile local state with exchange state
4. **Graceful Degradation**: Continue operation with reduced functionality when full recovery is not possible

### Database Recovery Example

```python
def load_bar_data(
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    start: datetime,
    end: datetime
) -> List[BarData]:
    """
    Load bar data from database.
    """
    with self.session_factory() as session:
        query = session.query(DbBarData)
        query = query.filter(
            DbBarData.symbol == symbol,
            DbBarData.exchange == exchange.value,
            DbBarData.interval == interval.value,
            DbBarData.datetime >= start,
            DbBarData.datetime <= end
        )
        
        bars = []
        for db_bar in query.all():
            bar = BarData(
                symbol=db_bar.symbol,
                exchange=Exchange(db_bar.exchange),
                datetime=db_bar.datetime,
                interval=Interval(db_bar.interval),
                volume=db_bar.volume,
                open_price=db_bar.open_price,
                high_price=db_bar.high_price,
                low_price=db_bar.low_price,
                close_price=db_bar.close_price,
                gateway_name="DB"
            )
            bars.append(bar)
        
        return bars
```

### Exchange Reconciliation

When reconnecting to an exchange, VeighNa reconciles local state with exchange state:

```python
def query_position(self):
    """
    Query position data from exchange.
    """
    pass

def query_account(self):
    """
    Query account data from exchange.
    """
    pass

def query_order(self):
    """
    Query order data from exchange.
    """
    pass
```

These methods are called when reconnecting to an exchange, and the returned data is used to update the local state.

## Thread Safety and Concurrency Considerations

VeighNa is designed to be thread-safe and handle concurrent access to state:

1. **Event-Driven Architecture**: Components communicate through events rather than direct state access
2. **Thread Synchronization**: Critical sections are protected by locks
3. **Immutable Data**: Many state objects are immutable
4. **Copy-on-Write**: State is copied before modification to avoid race conditions

### Thread Synchronization Example

```python
class PositionManager:
    """
    Position manager for tracking positions.
    """
    
    def __init__(self):
        """
        Initialize position manager.
        """
        self._positions = {}
        self._lock = Lock()
    
    def add_position(self, position: PositionData):
        """
        Add a position.
        """
        with self._lock:
            key = (position.symbol, position.exchange, position.direction)
            self._positions[key] = position
    
    def get_position(
        self,
        symbol: str,
        exchange: Exchange,
        direction: Direction
    ) -> PositionData:
        """
        Get a position.
        """
        with self._lock:
            key = (symbol, exchange, direction)
            return self._positions.get(key, None)
    
    def update_position(self, position: PositionData):
        """
        Update a position.
        """
        with self._lock:
            key = (position.symbol, position.exchange, position.direction)
            if key in self._positions:
                self._positions[key] = position
    
    def get_all_positions(self) -> List[PositionData]:
        """
        Get all positions.
        """
        with self._lock:
            return list(self._positions.values())
```

This approach ensures that state updates are atomic and consistent, even in a concurrent environment.
