"""
Data Preparation Module for VAR Model

This module handles loading and transforming the raw economic data into 
the variables needed for the VAR model:
- Monthly GDP Growth (%)
- CPI % Change (month-over-month)
- Bond Yield Spread (10-year minus 3-month rate)
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def load_data(filepath: str) -> pd.DataFrame:
    """
    Load the raw data from CSV.
    
    Args:
        filepath: Path to the dataocean.csv file
        
    Returns:
        DataFrame with raw data
    """
    df = pd.read_csv(filepath, index_col=0)
    return df


def calculate_gdp_growth(df: pd.DataFrame) -> pd.Series:
    """
    Calculate month-over-month GDP growth rate (%).
    
    Uses the Monthly Nominal GDP Index:
    Growth = ((GDP[t] - GDP[t-1]) / GDP[t-1]) * 100
    
    Args:
        df: DataFrame with 'Monthly Nominal GDP Index' column
        
    Returns:
        Series with monthly GDP growth rates
    """
    gdp_index = df['Monthly Nominal GDP Index'].copy()
    gdp_growth = gdp_index.pct_change() * 100
    return gdp_growth


def calculate_cpi_change(df: pd.DataFrame) -> pd.Series:
    """
    Calculate month-over-month CPI percentage change.
    
    Uses the CPIAUCSL column:
    CPI Change = ((CPI[t] - CPI[t-1]) / CPI[t-1]) * 100
    
    Args:
        df: DataFrame with 'CPIAUCSL' column
        
    Returns:
        Series with monthly CPI % changes
    """
    cpi = df['CPIAUCSL'].copy()
    cpi_change = cpi.pct_change() * 100
    return cpi_change


def calculate_yield_spread(df: pd.DataFrame) -> pd.Series:
    """
    Calculate bond yield spread (10-year minus 3-month rate).
    
    The spread captures the slope of the yield curve, which is important 
    for economic predictions.
    
    Yield Spread = 10 yr rate - 3 mo rate
    
    Args:
        df: DataFrame with '10 yr' and '3 mo' columns
        
    Returns:
        Series with yield spread values
    """
    rate_10yr = df['10 yr'].copy()
    rate_3mo = df['3 mo'].copy()
    
    # Calculate spread
    yield_spread = rate_10yr - rate_3mo
    
    return yield_spread


def prepare_var_data(filepath: str, verbose: bool = True) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare the complete VAR dataset with all three variables.
    
    This function:
    1. Loads the raw data
    2. Calculates all three VAR variables
    3. Removes rows with missing values
    4. Returns clean data ready for modeling
    
    Args:
        filepath: Path to the dataocean.csv file
        verbose: If True, print summary statistics
        
    Returns:
        Tuple of:
        - DataFrame with columns: 'gdp_growth', 'cpi_change', 'yield_spread'
        - Series with the date index
    """
    # Load data
    df = load_data(filepath)
    
    # Calculate variables
    gdp_growth = calculate_gdp_growth(df)
    cpi_change = calculate_cpi_change(df)
    yield_spread = calculate_yield_spread(df)
    
    # Combine into a single DataFrame
    var_data = pd.DataFrame({
        'gdp_growth': gdp_growth,
        'cpi_change': cpi_change,
        'yield_spread': yield_spread
    })
    
    # Try to get date index from original dataframe
    if 'date' in df.columns:
        var_data['date'] = df['date']
    
    # Remove rows with NaN values (first row will have NaN from pct_change)
    var_data_clean = var_data.dropna()
    
    if verbose:
        print("=" * 70)
        print("VAR Data Preparation Summary")
        print("=" * 70)
        print(f"\nDataset shape: {var_data_clean.shape}")
        print(f"Date range: {var_data_clean.index[0]} to {var_data_clean.index[-1]}")
        print(f"\nNumber of observations: {len(var_data_clean)}")
        print(f"\nDescriptive Statistics:")
        print(var_data_clean[['gdp_growth', 'cpi_change', 'yield_spread']].describe())
        print("\n" + "=" * 70)
    
    return var_data_clean, df


if __name__ == "__main__":
    # Example usage
    filepath = "../dataocean.csv"
    var_data, original_df = prepare_var_data(filepath, verbose=True)
    
    print("\nFirst few rows of VAR data:")
    print(var_data.head(10))
    
    print("\nData types:")
    print(var_data.dtypes)
