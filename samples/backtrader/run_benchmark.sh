#!/bin/bash

# Simple script to run the benchmark with UV
echo "Running Backtrader benchmark..."
cd "$(dirname "$0")"

# Run with UV 
uv run benchmark.py --data ../../data/BTCUSDT.csv "$@" 