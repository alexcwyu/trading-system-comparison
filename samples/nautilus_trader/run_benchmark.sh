#!/bin/bash
set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it first."
    echo "You can install it with: pip install uv"
    exit 1
fi

# Setup for the benchmark
echo "Setting up for the benchmark..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    # Force using Python 3.13 which is available on the system
    uv venv --python 3.13
    
    echo "Installing pip in virtual environment..."
    .venv/bin/python -m ensurepip --upgrade
    
    echo "Installing dependencies..."
    .venv/bin/python -m pip install -e .
fi

# Check if data directory exists
DATA_DIR="../../data"
if [ ! -d "$DATA_DIR" ]; then
    mkdir -p "$DATA_DIR"
fi

# Check if data file exists
DATA_FILE="$DATA_DIR/BTCUSDT_202401.csv"
if [ ! -f "$DATA_FILE" ]; then
    echo "Error: Data file $DATA_FILE not found."
    echo "Please ensure you have the required data file before running the benchmark."
    exit 1
fi

# Run the benchmark
echo "Running NautilusTrader benchmark..."
.venv/bin/python benchmark.py --data "$DATA_FILE" "$@" 