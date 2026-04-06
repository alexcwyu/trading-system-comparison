#!/bin/bash

# Script to run the Backtesting.py benchmark with UV
echo "Running Backtesting.py benchmark..."
cd "$(dirname "$0")"

# Default parameters
DATA_FILE="../../data/BTCUSDT_202401.csv"
START_DATE="2024-01-01"
END_DATE="2024-01-31"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --data)
            DATA_FILE="$2"
            shift 2
            ;;
        --start-date)
            START_DATE="$2"
            shift 2
            ;;
        --end-date)
            END_DATE="$2"
            shift 2
            ;;
        *)
            # Pass any other arguments directly to the script
            EXTRA_ARGS="${EXTRA_ARGS} $1"
            shift
            ;;
    esac
done

# Print configuration
echo "Data file: ${DATA_FILE}"
echo "Date range: ${START_DATE} to ${END_DATE}"
echo ""

# Run with UV 
uv run benchmark.py --data "${DATA_FILE}" --start-date "${START_DATE}" --end-date "${END_DATE}" ${EXTRA_ARGS} 