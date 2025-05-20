# Trading System Comparison Scripts

This directory contains utility scripts for the Trading System Comparison project.

## `extract_data.py`

This script extracts data from a CSV file within a specified date range. It's useful for preparing data for backtesting or analysis.

### Usage

```bash
./extract_data.py --input INPUT_FILE --output OUTPUT_FILE --from-date FROM_DATE [options]
```

### Parameters

- `--input` - Path to the input CSV file (required)
- `--output` - Path to the output CSV file (required)
- `--from-date` - Start date in YYYY-MM-DD format (required)
- `--to-date` - End date in YYYY-MM-DD format (optional, default: today)
- `--date-column` - Name of the date/timestamp column (optional, default: 'timestamp')
- `--header` - Flag to specify if a custom header should be added (optional)
- `--header-names` - Comma-separated list of column names for custom header (optional)

### Examples

1. Extract data for a specific date range using the default header:

```bash
./extract_data.py --input ../data/BTCUSDT.csv --output ../data/BTCUSDT_2024.csv --from-date 2024-01-01 --to-date 2024-12-31
```

2. Extract data from a start date until today:

```bash
./extract_data.py --input ../data/BTCUSDT.csv --output ../data/BTCUSDT_recent.csv --from-date 2023-01-01
```

3. Extract data with a custom header:

```bash
./extract_data.py --input ../data/BTCUSDT.csv --output ../data/BTCUSDT_custom.csv --from-date 2023-01-01 --header --header-names "timestamp,open,high,low,close,volume"
```

4. Use a different date column name:

```bash
./extract_data.py --input ../data/stock_data.csv --output ../data/stock_data_filtered.csv --from-date 2023-01-01 --date-column "date"
```

### Note

The script automatically handles:
- Converting date strings to datetime objects
- Creating the output directory if it doesn't exist
- Ensuring the date column is in the proper datetime format
- Error handling for missing columns or date ranges with no data 