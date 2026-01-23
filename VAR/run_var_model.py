"""
VAR Model - Complete Walkthrough and Execution Script

This script demonstrates how to:
1. Load and prepare the economic data
2. Build a VAR model
3. Optimize lag selection
4. Generate 24-month forecasts
5. Visualize and analyze results
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Import our custom modules
from data_preparation import prepare_var_data
from var_model import VARModelBuilder


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_step(step_num: int, description: str) -> None:
    """Print a formatted step header."""
    print(f"\n{'─' * 80}")
    print(f"STEP {step_num}: {description}")
    print(f"{'─' * 80}")


def main():
    """Execute the complete VAR workflow."""
    
    print_section("VECTOR AUTOREGRESSION (VAR) MODEL - COMPLETE WALKTHROUGH")
    
    # =====================================================================
    # STEP 1: Data Preparation
    # =====================================================================
    print_step(1, "Load and Prepare Data")
    
    print("""
This step loads the raw economic data and transforms it into three key variables:

1. GDP Growth (%):
   - Month-over-month percentage change in Nominal GDP Index
   - Formula: ((GDP[t] - GDP[t-1]) / GDP[t-1]) * 100
   - Measures: Economic growth rate

2. CPI Change (%):
   - Month-over-month percentage change in Consumer Price Index
   - Formula: ((CPI[t] - CPI[t-1]) / CPI[t-1]) * 100
   - Measures: Inflation rate

3. Yield Spread (basis points):
   - Difference between 10-year and 3-month bond yields
   - Formula: 10-year rate - 3-month rate
   - Measures: Term premium and economic expectations
    """)
    
    # Find the data file
    data_file = Path(__file__).parent.parent / "dataocean.csv"
    
    if not data_file.exists():
        print(f"ERROR: Could not find {data_file}")
        return
    
    print(f"Loading data from: {data_file}")
    var_data, original_df = prepare_var_data(str(data_file), verbose=True)
    
    # =====================================================================
    # STEP 2: Examine the Data
    # =====================================================================
    print_step(2, "Examine Prepared Data")
    
    print("\nFirst 10 rows:")
    print(var_data.head(10).to_string())
    
    print("\n\nLast 10 rows:")
    print(var_data.tail(10).to_string())
    
    print("\n\nCorrelation Matrix:")
    correlation = var_data[['gdp_growth', 'cpi_change', 'yield_spread']].corr()
    print(correlation.to_string())
    
    print("\n\nKey Statistics:")
    print(f"  Total observations: {len(var_data)}")
    print(f"  Time period: {var_data.index[0]} to {var_data.index[-1]}")
    print(f"  Variables: GDP Growth, CPI Change, Yield Spread")
    
    # =====================================================================
    # STEP 3: Build and Optimize VAR Model
    # =====================================================================
    print_step(3, "Build VAR Model and Select Optimal Lags")
    
    print("""
A VAR model is a system of regression equations where:
- Each variable is regressed on its own past values AND past values of all other variables
- The number of lags determines how much history influences current predictions
- Optimal lag selection balances model complexity with explanatory power

Common information criteria for lag selection:
- AIC (Akaike Information Criterion): Balances fit and complexity
- BIC (Bayesian Information Criterion): More conservative (penalizes complexity more)
- FPE (Final Prediction Error): Focus on forecast accuracy
- HQIC (Hannan-Quinn): Alternative information criterion

We'll select the lag that appears most frequently across these criteria.
    """)
    
    # Create model builder
    model = VARModelBuilder(var_data)
    
    # Select optimal lag
    lag_info = model.select_optimal_lag(maxlags=12)
    
    # =====================================================================
    # STEP 4: Fit the Model
    # =====================================================================
    print_step(4, "Fit VAR Model with Optimal Lags")
    
    print(f"""
Fitting a VAR({lag_info['optimal_lag']}) model using {len(var_data)} observations.

The model estimates how each variable depends on:
- Its own lagged values (past {lag_info['optimal_lag']} months)
- Lagged values of the other two variables

Total parameters to estimate: 3 variables × {lag_info['optimal_lag']} lags × 3 variables 
                              + 3 intercepts = {3*lag_info['optimal_lag']*3 + 3} parameters
    """)
    
    model.fit_model()
    
    # =====================================================================
    # STEP 5: Model Diagnostics
    # =====================================================================
    print_step(5, "Review Model Diagnostics")
    
    diagnostics = model.get_model_diagnostics()
    
    print(f"""
Model Quality Metrics:

Log-Likelihood: {diagnostics['log_likelihood']:.4f}
  - Higher values indicate better fit

Akaike Information Criterion (AIC): {diagnostics['aic']:.4f}
  - Lower values are better (balances fit and complexity)

Bayesian Information Criterion (BIC): {diagnostics['bic']:.4f}
  - Lower values are better (more conservative than AIC)

Forecast Prediction Error (FPE): {diagnostics['fpe']:.4f}
  - Estimates out-of-sample forecast accuracy

Hannan-Quinn Criterion (HQIC): {diagnostics['hqic']:.4f}
  - Balance between AIC and BIC

Observations Used: {diagnostics['num_obs']}
Parameters Estimated: {diagnostics['num_params']}
    """)
    
    # =====================================================================
    # STEP 6: Generate 24-Month Forecast
    # =====================================================================
    print_step(6, "Generate 24-Month Forecast")
    
    print("""
The forecast uses the fitted model to project:
- GDP Growth for the next 24 months
- CPI Change for the next 24 months  
- Yield Spread for the next 24 months

These projections are based on historical patterns in the data
and the estimated relationships between the variables.
    """)
    
    forecast = model.forecast(steps=24)
    
    # =====================================================================
    # STEP 7: Display and Analyze Results
    # =====================================================================
    print_step(7, "Analyze Forecast Results")
    
    print("\nDetailed 24-Month Forecast:")
    print(forecast.to_string())
    
    print("\n\n24-Month Forecast Summary:")
    print(forecast.describe().to_string())
    
    print("\n\nForecast Averages (What to expect):")
    print(f"  Average GDP Growth:     {forecast['gdp_growth'].mean():>8.4f}%")
    print(f"  Average CPI Change:     {forecast['cpi_change'].mean():>8.4f}%")
    print(f"  Average Yield Spread:   {forecast['yield_spread'].mean():>8.4f} basis points")
    
    print("\n\nForecast Ranges (Variation in predictions):")
    print(f"  GDP Growth:     {forecast['gdp_growth'].min():>8.4f}% to {forecast['gdp_growth'].max():>8.4f}%")
    print(f"  CPI Change:     {forecast['cpi_change'].min():>8.4f}% to {forecast['cpi_change'].max():>8.4f}%")
    print(f"  Yield Spread:   {forecast['yield_spread'].min():>8.4f} to {forecast['yield_spread'].max():>8.4f} bps")
    
    # =====================================================================
    # STEP 8: Save Results
    # =====================================================================
    print_step(8, "Save Results")
    
    output_file = Path(__file__).parent / "forecast_24month.csv"
    forecast.to_csv(output_file)
    print(f"✓ Forecast saved to: {output_file}")
    
    # Also save a summary report
    report_file = Path(__file__).parent / "model_summary.txt"
    with open(report_file, 'w') as f:
        f.write("VAR MODEL SUMMARY REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Observations used: {len(var_data)}\n")
        f.write(f"Variables: GDP Growth, CPI Change, Yield Spread\n")
        f.write(f"Lag order: {lag_info['optimal_lag']}\n\n")
        f.write("MODEL EQUATION:\n")
        f.write(model.summary())
        f.write("\n\n24-MONTH FORECAST:\n")
        f.write(forecast.to_string())
    
    print(f"✓ Model summary saved to: {report_file}")
    
    # =====================================================================
    # FINAL SUMMARY
    # =====================================================================
    print_section("WORKFLOW COMPLETE")
    
    print(f"""
Summary of Results:
- Successfully loaded and prepared economic data
- Built a VAR({lag_info['optimal_lag']}) model with {len(var_data)} observations
- Generated 24-month forecasts for all three variables
- Saved results to CSV and text files

Files created:
  • forecast_24month.csv - Raw forecast data
  • model_summary.txt - Detailed model information

Key Insights:
- GDP Growth Forecast: {forecast['gdp_growth'].mean():.2f}% average monthly growth
- Inflation Forecast: {forecast['cpi_change'].mean():.2f}% average monthly inflation
- Term Premium: {forecast['yield_spread'].mean():.2f} basis points average

Next Steps:
- Review the forecast results in the CSV file
- Use the model for scenario analysis
- Consider adding additional variables
- Monitor forecast accuracy as new data arrives
    """)
    
    return model, forecast, var_data


if __name__ == "__main__":
    model, forecast, var_data = main()
    
    print("\n✓ Script completed successfully!")
    print("\nVariables available for further analysis:")
    print("  - model: VARModelBuilder object with fitted model")
    print("  - forecast: 24-month forecast DataFrame")
    print("  - var_data: Prepared VAR data used for modeling")
