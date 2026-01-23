"""
VAR Model Module

This module handles:
- Building the Vector Autoregression (VAR) model
- Optimizing lag selection
- Generating forecasts for 24 months ahead
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR
from typing import Tuple, Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class VARModelBuilder:
    """Build and manage VAR model for economic forecasting."""
    
    def __init__(self, data: pd.DataFrame, variable_columns: List[str] = None):
        """
        Initialize the VAR model builder.
        
        Args:
            data: DataFrame with time series data
            variable_columns: List of column names to use in VAR model.
                            Default: ['gdp_growth', 'cpi_change', 'yield_spread']
        """
        self.data = data.copy()
        
        if variable_columns is None:
            variable_columns = ['gdp_growth', 'cpi_change', 'yield_spread']
        
        self.variable_columns = variable_columns
        self.model = None
        self.results = None
        self.optimal_lag = None
        
        # Extract only the required columns
        self.var_data = self.data[variable_columns].copy()
    
    def select_optimal_lag(self, maxlags: int = 12) -> Dict:
        """
        Select optimal lag order using multiple criteria.
        
        Tests lags from 1 to maxlags and compares using:
        - Akaike Information Criterion (AIC)
        - Bayesian Information Criterion (BIC)
        - Final Prediction Error (FPE)
        - Hannan-Quinn Information Criterion (HQIC)
        
        Args:
            maxlags: Maximum number of lags to test
            
        Returns:
            Dictionary with lag selection results and diagnostics
        """
        print("Selecting optimal lag order...")
        print("-" * 70)
        
        model = VAR(self.var_data)
        
        # Test different lag lengths
        criteria_results = {}
        for lag in range(1, maxlags + 1):
            res = model.fit(lag)
            criteria_results[lag] = {
                'aic': res.aic,
                'bic': res.bic,
                'fpe': res.fpe,
                'hqic': res.hqic
            }
        
        print("\nLag Selection Criteria:")
        print(f"{'Lag':<5} {'AIC':<12} {'BIC':<12} {'FPE':<12} {'HQIC':<12}")
        print("-" * 53)
        for lag, crit in criteria_results.items():
            print(f"{lag:<5} {crit['aic']:<12.4f} {crit['bic']:<12.4f} {crit['fpe']:<12.4f} {crit['hqic']:<12.4f}")
        
        # Find lag with minimum criterion value for each
        aic_lag = min(criteria_results, key=lambda x: criteria_results[x]['aic'])
        bic_lag = min(criteria_results, key=lambda x: criteria_results[x]['bic'])
        fpe_lag = min(criteria_results, key=lambda x: criteria_results[x]['fpe'])
        hqic_lag = min(criteria_results, key=lambda x: criteria_results[x]['hqic'])
        
        # Most conservative approach: use the most frequently suggested lag
        lag_suggestions = [aic_lag, bic_lag, fpe_lag, hqic_lag]
        self.optimal_lag = max(set(lag_suggestions), key=lag_suggestions.count)
        
        print(f"\nCriterion-specific recommendations:")
        print(f"  AIC suggests lag {aic_lag}")
        print(f"  BIC suggests lag {bic_lag}")
        print(f"  FPE suggests lag {fpe_lag}")
        print(f"  HQIC suggests lag {hqic_lag}")
        
        print(f"\nOptimal lag order selected: {self.optimal_lag}")
        print(f"(Most commonly suggested across information criteria)")
        
        return {
            'optimal_lag': self.optimal_lag,
            'criteria_results': criteria_results,
            'aic_lag': aic_lag,
            'bic_lag': bic_lag,
            'fpe_lag': fpe_lag,
            'hqic_lag': hqic_lag
        }
    
    def fit_model(self, lag_order: Optional[int] = None) -> None:
        """
        Fit the VAR model with specified lag order.
        
        Args:
            lag_order: Number of lags to use. If None, uses optimal_lag.
                      If optimal_lag not set, uses lag_order=2 as default.
        """
        if lag_order is None:
            if self.optimal_lag is None:
                print("Optimal lag not selected. Using default lag_order=2")
                lag_order = 2
            else:
                lag_order = self.optimal_lag
        
        print(f"\nFitting VAR model with {lag_order} lags...")
        print("-" * 70)
        
        self.model = VAR(self.var_data)
        self.results = self.model.fit(lag_order)
        
        print(self.results.summary())
    
    def get_model_diagnostics(self) -> Dict:
        """
        Get key diagnostic statistics from fitted model.
        
        Returns:
            Dictionary with key model diagnostics
        """
        if self.results is None:
            raise ValueError("Model must be fitted first. Call fit_model()")
        
        diagnostics = {
            'log_likelihood': self.results.llf,
            'aic': self.results.aic,
            'bic': self.results.bic,
            'fpe': self.results.fpe,
            'hqic': self.results.hqic,
            'num_obs': self.results.nobs,
            'num_params': self.results.k_ar * len(self.variable_columns) + len(self.variable_columns)
        }
        
        return diagnostics
    
    def forecast(self, steps: int = 24) -> pd.DataFrame:
        """
        Generate forecasts for specified number of steps ahead.
        
        Args:
            steps: Number of months to forecast (default: 24)
            
        Returns:
            DataFrame with forecasted values for each variable
        """
        if self.results is None:
            raise ValueError("Model must be fitted first. Call fit_model()")
        
        print(f"\nGenerating {steps}-step ahead forecast...")
        print("-" * 70)
        
        # Use the forecast method available in VARResults
        forecast_values = self.results.forecast(self.var_data.values[-self.results.k_ar:], steps=steps)
        
        # Create forecast DataFrame with proper column names
        forecast_df = pd.DataFrame(
            forecast_values,
            columns=self.variable_columns,
            index=pd.RangeIndex(1, steps + 1)
        )
        
        forecast_df.index.name = 'forecast_month'
        
        print(f"Forecast generated for {steps} months")
        print("\nForecast summary:")
        print(forecast_df.describe())
        
        return forecast_df
    
    def get_impulse_response(self, periods: int = 10) -> Dict:
        """
        Calculate impulse response functions (IRF).
        
        Shows how shocks to one variable affect all variables over time.
        
        Args:
            periods: Number of periods to calculate IRF for
            
        Returns:
            Dictionary containing IRF data
        """
        if self.results is None:
            raise ValueError("Model must be fitted first. Call fit_model()")
        
        irf = self.results.irf(periods)
        
        return {
            'irfs': irf.irfs,
            'variable_names': self.variable_columns,
            'periods': periods
        }
    
    def get_forecast_error_variance_decomposition(self, periods: int = 24) -> pd.DataFrame:
        """
        Calculate forecast error variance decomposition (FEVD).
        
        Shows the proportion of forecast error variance for each variable
        that comes from shocks to each variable.
        
        Args:
            periods: Number of periods to calculate FEVD for
            
        Returns:
            FEVD results
        """
        if self.results is None:
            raise ValueError("Model must be fitted first. Call fit_model()")
        
        fevd = self.results.fevd(periods)
        
        return fevd
    
    def summary(self) -> str:
        """Get full model summary."""
        if self.results is None:
            return "Model not yet fitted"
        return str(self.results.summary())


def quick_forecast(data: pd.DataFrame, 
                   forecast_steps: int = 24,
                   lag_order: int = 2,
                   variable_columns: List[str] = None) -> pd.DataFrame:
    """
    Convenience function for quick VAR forecasting.
    
    Args:
        data: DataFrame with VAR data
        forecast_steps: Number of months to forecast
        lag_order: Number of lags to use
        variable_columns: Columns to use in model
        
    Returns:
        DataFrame with forecasts
    """
    builder = VARModelBuilder(data, variable_columns)
    builder.fit_model(lag_order=lag_order)
    forecast = builder.forecast(steps=forecast_steps)
    
    return forecast


if __name__ == "__main__":
    # Example usage would go here
    pass
