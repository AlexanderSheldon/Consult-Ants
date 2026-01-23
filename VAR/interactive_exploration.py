"""
Interactive VAR Model Exploration Script

Use this script to interactively explore the VAR model, generate custom
forecasts, and perform various analyses.

Run with: python interactive_exploration.py
"""

import pandas as pd
import numpy as np
from data_preparation import prepare_var_data
from var_model import VARModelBuilder
from utils import (
    multi_step_forecast, 
    compare_scenarios,
    save_model, 
    load_model,
    calculate_forecast_confidence_intervals
)


def print_menu():
    """Display the interactive menu."""
    print("\n" + "=" * 70)
    print("VAR MODEL INTERACTIVE EXPLORER")
    print("=" * 70)
    print("\n1. Load and prepare data")
    print("2. Build VAR model with custom lag selection")
    print("3. View model summary and diagnostics")
    print("4. Generate 24-month forecast")
    print("5. Generate multi-horizon forecasts (12, 24, 36 months)")
    print("6. Analyze forecast confidence intervals")
    print("7. Compare economic scenarios")
    print("8. Save model for later use")
    print("9. View current data statistics")
    print("0. Exit")
    print("\n" + "=" * 70)


def option_1_prepare_data(var_data=None):
    """Load and prepare data."""
    print("\nLoading and preparing data...")
    var_data, original_df = prepare_var_data("../dataocean.csv", verbose=True)
    return var_data, original_df


def option_2_build_model(var_data):
    """Build VAR model with custom parameters."""
    if var_data is None:
        print("No data loaded. Please load data first (option 1).")
        return None
    
    print("\n" + "-" * 70)
    print("Building VAR Model")
    print("-" * 70)
    
    maxlags = input("\nEnter maximum lags to test (default 12): ").strip()
    maxlags = int(maxlags) if maxlags else 12
    
    model = VARModelBuilder(var_data)
    model.select_optimal_lag(maxlags=maxlags)
    
    use_optimal = input("\nUse optimal lag? (y/n, default y): ").strip().lower()
    
    if use_optimal in ['n', 'no']:
        lag = input("Enter lag order to use: ").strip()
        lag = int(lag)
    else:
        lag = None
    
    model.fit_model(lag_order=lag)
    
    print("\n✓ Model fitted successfully!")
    return model


def option_3_model_summary(model):
    """Display model summary and diagnostics."""
    if model is None or model.results is None:
        print("No model fitted. Please build model first (option 2).")
        return
    
    print("\n" + "-" * 70)
    print("MODEL SUMMARY AND DIAGNOSTICS")
    print("-" * 70)
    
    print("\nModel Equations:")
    print(model.summary())
    
    print("\n\nModel Diagnostics:")
    diagnostics = model.get_model_diagnostics()
    for key, value in diagnostics.items():
        if isinstance(value, float):
            print(f"  {key:.<40} {value:.4f}")
        else:
            print(f"  {key:.<40} {value}")


def option_4_forecast_24m(model):
    """Generate 24-month forecast."""
    if model is None or model.results is None:
        print("No model fitted. Please build model first (option 2).")
        return None
    
    print("\n" + "-" * 70)
    forecast = model.forecast(steps=24)
    
    print("\nForecast Statistics:")
    print(forecast.describe().to_string())
    
    save_csv = input("\nSave forecast to CSV? (y/n): ").strip().lower()
    if save_csv in ['y', 'yes']:
        filename = input("Filename (default: forecast_24month_custom.csv): ").strip()
        filename = filename if filename else "forecast_24month_custom.csv"
        forecast.to_csv(filename)
        print(f"✓ Saved to {filename}")
    
    return forecast


def option_5_multi_horizon(model):
    """Generate multi-horizon forecasts."""
    if model is None or model.results is None:
        print("No model fitted. Please build model first (option 2).")
        return
    
    print("\n" + "-" * 70)
    print("Generating multi-horizon forecasts...")
    
    forecasts = multi_step_forecast(model, steps_list=[12, 24, 36])
    
    for horizon, forecast in forecasts.items():
        print(f"\n{horizon}-Month Forecast:")
        print(f"  GDP Growth:    {forecast['gdp_growth'].mean():.4f}% avg, range: {forecast['gdp_growth'].min():.4f}% to {forecast['gdp_growth'].max():.4f}%")
        print(f"  CPI Change:    {forecast['cpi_change'].mean():.4f}% avg, range: {forecast['cpi_change'].min():.4f}% to {forecast['cpi_change'].max():.4f}%")
        print(f"  Yield Spread:  {forecast['yield_spread'].mean():.4f} avg, range: {forecast['yield_spread'].min():.4f} to {forecast['yield_spread'].max():.4f}")


def option_6_confidence_intervals(model):
    """Analyze forecast confidence intervals."""
    if model is None or model.results is None:
        print("No model fitted. Please build model first (option 2).")
        return
    
    print("\n" + "-" * 70)
    print("Calculating forecast confidence intervals...")
    
    steps = input("Forecast horizon (default 24): ").strip()
    steps = int(steps) if steps else 24
    
    confidence = input("Confidence level (0-1, default 0.95): ").strip()
    confidence = float(confidence) if confidence else 0.95
    
    point_forecast, lower, upper = calculate_forecast_confidence_intervals(
        model, steps=steps, confidence=confidence
    )
    
    print(f"\n{confidence*100:.0f}% Confidence Intervals for {steps} months:")
    print("\nGDP Growth (%):")
    print(f"  Point Forecast: {point_forecast['gdp_growth'].mean():.4f}%")
    print(f"  Range:          {lower['gdp_growth'].mean():.4f}% to {upper['gdp_growth'].mean():.4f}%")
    
    print("\nCPI Change (%):")
    print(f"  Point Forecast: {point_forecast['cpi_change'].mean():.4f}%")
    print(f"  Range:          {lower['cpi_change'].mean():.4f}% to {upper['cpi_change'].mean():.4f}%")
    
    print("\nYield Spread:")
    print(f"  Point Forecast: {point_forecast['yield_spread'].mean():.4f}")
    print(f"  Range:          {lower['yield_spread'].mean():.4f} to {upper['yield_spread'].mean():.4f}")


def option_7_scenarios(model, var_data):
    """Compare economic scenarios."""
    if model is None or model.results is None:
        print("No model fitted. Please build model first (option 2).")
        return
    
    if var_data is None:
        print("No data loaded. Please load data first (option 1).")
        return
    
    print("\n" + "-" * 70)
    print("Scenario Analysis")
    print("-" * 70)
    
    print("\nPredefined scenarios:")
    print("1. High Inflation: +0.5% CPI shock")
    print("2. Recession: -0.5% GDP shock")
    print("3. Yield Inversion: -1% yield spread shock")
    print("4. Custom scenario")
    
    choice = input("Select scenario (1-4): ").strip()
    
    scenarios = {}
    
    if choice == '1':
        scenarios['high_inflation'] = {'cpi_change': 0.5}
    elif choice == '2':
        scenarios['recession'] = {'gdp_growth': -0.5}
    elif choice == '3':
        scenarios['yield_inversion'] = {'yield_spread': -1.0}
    elif choice == '4':
        scenario_name = input("Scenario name: ").strip()
        var_shock = input("Variable to shock (gdp_growth/cpi_change/yield_spread): ").strip()
        shock_value = float(input("Shock magnitude: ").strip())
        scenarios[scenario_name] = {var_shock: shock_value}
    else:
        print("Invalid choice")
        return
    
    print("\nComparing scenarios...")
    results = compare_scenarios(var_data, scenarios, model)
    
    for scenario_name, forecast in results.items():
        print(f"\n{scenario_name.upper()}:")
        print(f"  GDP Growth average:  {forecast['gdp_growth'].mean():.4f}%")
        print(f"  CPI Change average:  {forecast['cpi_change'].mean():.4f}%")
        print(f"  Yield Spread average: {forecast['yield_spread'].mean():.4f}")


def option_8_save_model(model):
    """Save model for later use."""
    if model is None or model.results is None:
        print("No model fitted. Please build model first (option 2).")
        return
    
    print("\n" + "-" * 70)
    filename = input("Filename to save (default: var_model.pkl): ").strip()
    filename = filename if filename else "var_model.pkl"
    
    save_model(model, filename)
    print(f"✓ Model saved to {filename}")


def option_9_data_stats(var_data):
    """Display data statistics."""
    if var_data is None:
        print("No data loaded. Please load data first (option 1).")
        return
    
    print("\n" + "-" * 70)
    print("DATA STATISTICS")
    print("-" * 70)
    
    print("\nDescriptive Statistics:")
    print(var_data[['gdp_growth', 'cpi_change', 'yield_spread']].describe().to_string())
    
    print("\n\nCorrelation Matrix:")
    print(var_data[['gdp_growth', 'cpi_change', 'yield_spread']].corr().to_string())
    
    print(f"\n\nData Range: {len(var_data)} observations")
    print(f"Period: {var_data.index[0]} to {var_data.index[-1]}")


def main():
    """Main interactive loop."""
    var_data = None
    original_df = None
    model = None
    
    print("\nWelcome to the VAR Model Interactive Explorer!")
    
    while True:
        print_menu()
        choice = input("Enter your choice (0-9): ").strip()
        
        if choice == '0':
            print("\nGoodbye!")
            break
        
        elif choice == '1':
            var_data, original_df = option_1_prepare_data(var_data)
        
        elif choice == '2':
            model = option_2_build_model(var_data)
        
        elif choice == '3':
            option_3_model_summary(model)
        
        elif choice == '4':
            option_4_forecast_24m(model)
        
        elif choice == '5':
            option_5_multi_horizon(model)
        
        elif choice == '6':
            option_6_confidence_intervals(model)
        
        elif choice == '7':
            option_7_scenarios(model, var_data)
        
        elif choice == '8':
            option_8_save_model(model)
        
        elif choice == '9':
            option_9_data_stats(var_data)
        
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
