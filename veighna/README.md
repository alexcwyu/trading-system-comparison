# VeighNa Trading System

## Overview

VeighNa is a Python-based quantitative trading platform that provides a comprehensive framework for developing, testing, and deploying trading strategies. It offers a modular architecture with multiple specialized applications for different trading scenarios, including CTA strategies, algorithmic trading, options trading, and more.

VeighNa is designed to be user-friendly while still offering advanced features for professional traders. It provides both a graphical user interface (VeighNa Trader) and a programmatic interface for strategy development and execution.

## Architecture

![VeighNa Architecture](./images/veighna-architecture.png)

VeighNa's architecture consists of several key components:

1. **Core Engine** - The central component that coordinates all activities
2. **Event Engine** - Event-driven architecture for handling market data and trading events
3. **Gateway** - Interfaces to various trading venues (exchanges, brokers)
4. **Applications** - Specialized modules for different trading scenarios
5. **GUI** - Graphical user interface for user interaction

## Key Components and Relationships

### Core Engine

The `MainEngine` is the central component that coordinates all activities:
- Manages gateways for market data and trading
- Handles event distribution
- Coordinates application modules
- Manages data persistence

### Event Engine

The `EventEngine` implements an event-driven architecture:
- Processes events in a separate thread
- Distributes events to registered handlers
- Supports both synchronous and asynchronous event processing
- Provides event queuing and prioritization

### Gateway

Gateways provide interfaces to various trading venues:
- Connect to exchanges and brokers
- Handle market data subscription and processing
- Execute trading orders
- Manage account information

### Applications

VeighNa provides multiple specialized applications:
- **CTA Strategy**: For trend-following and mean-reversion strategies
- **Spread Trading**: For multi-contract spread trading
- **Algorithmic Trading**: For smart order execution
- **Option Master**: For options trading with volatility analysis
- **Portfolio Strategy**: For multi-instrument portfolio strategies
- **Script Trader**: For script-based trading strategies

### GUI

The VeighNa Trader GUI provides:
- Market data display
- Order management
- Position monitoring
- Strategy configuration and monitoring
- Performance analysis

## Supported Markets and Instruments

VeighNa supports a wide range of markets and instruments through its gateway system:

- **Chinese Markets**: Stock, Futures, Options
- **Global Markets**: Forex, Crypto, International Futures
- **Custom Markets**: User-defined markets and instruments

## Performance Characteristics

- **Execution Speed**: Millisecond-level response times
- **Memory Efficiency**: Optimized for long-running processes
- **Concurrency**: Multi-threaded event processing
- **Scalability**: Modular design allows for scaling specific components

## Dependencies and Requirements

- Python 3.7 or higher
- PyQt5 for GUI components
- NumPy, pandas for data analysis
- TA-Lib for technical analysis
- SQLite or MySQL for data storage

## Quick Start Guide

### Installation

```bash
# Install VeighNa
pip install vnpy

# Install gateway modules
pip install vnpy_ctp  # CTP gateway for Chinese futures
pip install vnpy_ib   # Interactive Brokers gateway
pip install vnpy_binance  # Binance gateway for crypto

# Install application modules
pip install vnpy_ctastrategy  # CTA strategy module
pip install vnpy_spreadtrading  # Spread trading module
pip install vnpy_algotrading  # Algorithmic trading module
```

### Basic Usage

```python
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

# Import gateway and app modules
from vnpy_ctp import CtpGateway
from vnpy_ctastrategy import CtaStrategyApp

# Create application
qapp = create_qapp()
event_engine = EventEngine()
main_engine = MainEngine(event_engine)

# Add gateway and apps
main_engine.add_gateway(CtpGateway)
main_engine.add_app(CtaStrategyApp)

# Create and show main window
main_window = MainWindow(main_engine, event_engine)
main_window.showMaximized()

# Run application
qapp.exec()
```

For more detailed examples, see the [event-flow.md](./event-flow.md), [state-management.md](./state-management.md), and [handlers.md](./handlers.md) documentation.
