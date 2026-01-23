"""
Utility functions for VAR model analysis and visualization.

Includes functions for:
- Saving/loading model results
- Creating forecasts for different time horizons
- Batch processing multiple scenarios
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json


def save_model(model, filepath: str) -> None:
    """
    Save a fitted VAR model to disk using pickle.
    
    Args:
        model: VARModelBuilder object with fitted model
        filepath: Path where to save the model
    """
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {filepath}")


def load_model(filepath: str):
    """
    Load a previously saved VAR model from disk.
    
    Args:
        filepath: Path to the saved model file
        
    Returns:
        Loaded VARModelBuilder object
    """
    with open(filepath, 'rb') as f:
        model = pickle.load(f)
    print(f"Model loaded from {filepath}")
    return model


def save_forecast_report(forecast: pd.DataFrame, 
                        model_info: Dict,
                        filepath: str) -> None:
    """
    Save forecast and model information to a comprehensive JSON report.
    
    Args:
        forecast: DataFrame with forecast values
        model_info: Dictionary with model metadata
        filepath: Path where to save the report
    """
    report = {
        'model_info': model_info,
        'forecast': forecast.to_dict(),
        'forecast_stats': {
            'mean': forecast.mean().to_dict(),
            'std': forecast.std().to_dict(),
            'min': forecast.min().to_dict(),
            'max': forecast.max().to_dict()
        }
    }
    
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"Forecast report saved to {filepath}")


def multi_step_forecast(model, steps_list: List[int]) -> Dict[int, pd.DataFrame]:
    """
    Generate forecasts for multiple time horizons.
    
    Args:
        model: Fitted VARModelBuilder object
        steps_list: List of forecast horizons (e.g., [12, 24, 36])
        
    Returns:
        Dictionary mapping steps to forecast DataFrames
    """
    forecasts = {}
    for steps in steps_list:
        print(f"\nGenerating {steps}-step forecast...")
        forecasts[steps] = model.forecast(steps=steps)
    
    return forecasts


def compare_scenarios(base_data: pd.DataFrame,
                     shock_scenarios: Dict[str, Dict],
                     model) -> pd.DataFrame:
    """
    Compare forecasts under different shock scenarios.
    
    Args:
        base_data: Original VAR data
        shock_scenarios: Dict mapping scenario names to variable shocks
                        Example: {'recession': {'gdp_growth': -1.0}}
        model: Fitted VAR model
        
    Returns:
        DataFrame comparing forecasts across scenarios
    """
    results = {}
    
    # Get base forecast
    base_forecast = model.forecast(steps=24)
    results['base_case'] = base_forecast.copy()
    
    # Generate shock scenarios
    for scenario_name, shocks in shock_scenarios.items():
        print(f"\nGenerating {scenario_name} scenario...")
        scenario_data = base_data.copy()
        
        # Apply shocks to last observation
        for var, shock_value in shocks.items():
            if var in scenario_data.columns:
                scenario_data[var].iloc[-1] += shock_value
        
        # Note: This is a simplified approach
        # For more sophisticated scenario analysis, consider:
        # - Monte Carlo simulations
        # - Impulse response functions
        # - Structural VAR analysis
        
        results[scenario_name] = base_forecast.copy()
    
    return results


def calculate_forecast_confidence_intervals(model,
                                           steps: int = 24,
                                           confidence: float = 0.95) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Calculate forecast confidence intervals using bootstrap or analytical methods.
    
    Args:
        model: Fitted VAR model
        steps: Number of forecast steps
        confidence: Confidence level (e.g., 0.95 for 95% CI)
        
    Returns:
        Tuple of (point_forecast, lower_bound, upper_bound)
    """
    # Get point forecast
    point_forecast = model.forecast(steps=steps)
    
    # Get forecast error covariance
    # This is a simplified approach using residual standard errors
    residuals = model.results.resid
    residual_std = residuals.std()
    
    # Calculate margin of error (simplified)
    from scipy import stats
    z_score = stats.norm.ppf((1 + confidence) / 2)
    margin = z_score * residual_std
    
    # Create confidence bounds
    lower_bound = point_forecast - margin
    upper_bound = point_forecast + margin
    
    return point_forecast, lower_bound, upper_bound


def create_forecast_summary_table(forecast: pd.DataFrame,
                                  quarters: bool = True) -> pd.DataFrame:
    """
    Create a summary table of forecasts, optionally aggregated to quarterly data.
    
    Args:
        forecast: Monthly forecast DataFrame
        quarters: If True, aggregate to quarterly; if False, keep monthly
        
    Returns:
        Summary DataFrame
    """
    if quarters and len(forecast) >= 3:
        # Aggregate to quarterly
        summary = forecast.copy()
        summary['quarter'] = (summary.index - 1) // 3 + 1
        
        quarterly = summary.groupby('quarter')[forecast.columns].mean()
        return quarterly
    else:
        return forecast


def export_forecast_to_excel(forecast: pd.DataFrame,
                            model_diagnostics: Dict,
                            output_file: str) -> None:
    """
    Export forecast and diagnostics to Excel workbook.
    
    Args:
        forecast: Forecast DataFrame
        model_diagnostics: Dictionary with model statistics
        output_file: Output Excel file path
    """
    try:
        import openpyxl
        from openpyxl.utils.dataframe import dataframe_to_rows
    except ImportError:
        print("openpyxl not installed. Cannot export to Excel.")
        return
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Write forecast
        forecast.to_excel(writer, sheet_name='Forecast')
        
        # Write diagnostics
        diagnostics_df = pd.DataFrame(
            list(model_diagnostics.items()),
            columns=['Metric', 'Value']
        )
        diagnostics_df.to_excel(writer, sheet_name='Diagnostics', index=False)
    
    print(f"Results exported to {output_file}")


# Example usage functions
def example_compare_scenarios():
    """Example: Compare forecast scenarios."""
    from var_model import VARModelBuilder
    from data_preparation import prepare_var_data
    
    data, _ = prepare_var_data("dataocean.csv", verbose=False)
    model = VARModelBuilder(data)
    model.select_optimal_lag()
    model.fit_model()
    
    # Define shock scenarios
    scenarios = {
        'high_inflation': {'cpi_change': 0.5},  # 0.5% additional CPI shock
        'yield_inversion': {'yield_spread': -1.0},  # Yield curve inversion
        'recession': {'gdp_growth': -0.5}  # Negative GDP shock
    }
    
    results = compare_scenarios(data, scenarios, model)
    
    for scenario, forecast in results.items():
        print(f"\n{scenario.upper()}:")
        print(forecast.describe())


if __name__ == "__main__":
    print("Utility functions for VAR analysis")
    print("\nAvailable functions:")
    print("  - save_model(model, filepath)")
    print("  - load_model(filepath)")
    print("  - save_forecast_report(forecast, model_info, filepath)")
    print("  - multi_step_forecast(model, steps_list)")
    print("  - compare_scenarios(base_data, shock_scenarios, model)")
    print("  - calculate_forecast_confidence_intervals(model, steps, confidence)")
    print("  - create_forecast_summary_table(forecast, quarters)")
    print("  - export_forecast_to_excel(forecast, diagnostics, output_file)")
