#!/usr/bin/env python
# coding: utf-8

"""
Data extraction script for trading data.

This script extracts data from a CSV file within a specified date range.
It can be used to prepare data for backtesting or analysis.
"""

import os
import argparse
import pandas as pd
from datetime import datetime, date

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Extract data within a date range')
    
    parser.add_argument('--input', type=str, required=True,
                        help='Path to the input CSV file')
    
    parser.add_argument('--output', type=str, required=True,
                        help='Path to the output CSV file')
    
    parser.add_argument('--from-date', type=str, required=True,
                        help='Start date (YYYY-MM-DD)')
    
    parser.add_argument('--to-date', type=str, default=None,
                        help='End date (YYYY-MM-DD, default: today)')
    
    parser.add_argument('--date-column', type=str, default='timestamp',
                        help='Name of the date/timestamp column (default: timestamp)')
    
    parser.add_argument('--header', action='store_true',
                        help='Specify if a custom header should be added (uses existing header by default)')
    
    parser.add_argument('--header-names', type=str, default=None,
                        help='Comma-separated list of column names for custom header')
    
    return parser.parse_args()

def extract_data(input_file, output_file, from_date, to_date=None, date_column='timestamp', 
                 custom_header=False, header_names=None):
    """
    Extract data from a CSV file within a specified date range.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to the output CSV file
        from_date (str): Start date (YYYY-MM-DD)
        to_date (str, optional): End date (YYYY-MM-DD), defaults to today
        date_column (str, optional): Name of the date/timestamp column
        custom_header (bool, optional): Whether to use a custom header
        header_names (str, optional): Comma-separated list of column names for custom header
    """
    print(f"Extracting data from {input_file}")
    
    # Convert date strings to datetime objects
    from_date = pd.to_datetime(from_date)
    to_date = pd.to_datetime(to_date) if to_date else pd.to_datetime(date.today())
    
    # Read the input file
    try:
        # First try reading with auto header detection
        df = pd.read_csv(input_file, parse_dates=[date_column])
    except ValueError:
        # If that fails, try reading with no header
        print(f"Could not parse header. Trying with no header...")
        df = pd.read_csv(input_file, header=None, parse_dates=[0])
        df.rename(columns={0: date_column}, inplace=True)
        
        # If custom header names are provided, use them
        if header_names:
            column_names = header_names.split(',')
            if len(column_names) != len(df.columns):
                print(f"Warning: Number of provided column names ({len(column_names)}) "
                      f"doesn't match number of columns in the file ({len(df.columns)})")
                # Use as many as possible
                for i, name in enumerate(column_names):
                    if i < len(df.columns):
                        df.rename(columns={i: name.strip()}, inplace=True)
    
    # Ensure the date column is in datetime format
    if date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column])
    else:
        raise ValueError(f"Column '{date_column}' not found in the input file")
    
    # Filter the data based on the date range
    filtered_df = df[(df[date_column] >= from_date) & (df[date_column] <= to_date)]
    
    # Check if we have any data
    if len(filtered_df) == 0:
        print(f"Warning: No data found in the specified date range "
              f"({from_date.date()} to {to_date.date()})")
    else:
        print(f"Extracted {len(filtered_df)} rows of data from "
              f"{filtered_df[date_column].min().date()} to {filtered_df[date_column].max().date()}")
    
    # Create the output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Write the filtered data to the output file
    filtered_df.to_csv(output_file, index=False)
    print(f"Data written to {output_file}")

def main():
    """Main function."""
    args = parse_args()
    
    extract_data(
        input_file=args.input,
        output_file=args.output,
        from_date=args.from_date,
        to_date=args.to_date,
        date_column=args.date_column,
        custom_header=args.header,
        header_names=args.header_names
    )

if __name__ == "__main__":
    main() 