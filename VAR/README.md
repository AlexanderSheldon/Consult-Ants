# Vector Autoregression (VAR) Model for Economic Forecasting

## Overview

This folder contains a complete implementation of a **Vector Autoregression (VAR)** model for forecasting key economic indicators 24 months into the future. The model analyzes three interconnected economic variables:

1. **GDP Growth (%)** - Monthly percentage change in nominal GDP
2. **CPI Change (%)** - Monthly inflation rate measured by CPI  
3. **Yield Spread** - Difference between 10-year and 3-month bond yields

## What is a VAR Model?

A Vector Autoregression model is a multivariate time series model that captures:

- **Autocorrelation**: How each variable depends on its own past values
- **Cross-variable relationships**: How each variable is influenced by past values of other variables
- **System dynamics**: The joint evolution of multiple related time series

### Key Formula

For a VAR(p) model with 3 variables:

```
Y_t = c + A₁Y_{t-1} + A₂Y_{t-2} + ... + AₚY_{t-p} + u_t

Where:
- Y_t = vector of current values [gdp_growth, cpi_change, yield_spread]
- c = constant term
- A₁...Aₚ = coefficient matrices for each lag
- p = lag order (determined by information criteria)
- u_t = error term (contemporaneously correlated)
```

## Project Structure

```
VAR/
├── data_preparation.py      # Load and transform raw data
├── var_model.py            # VAR model implementation
├── utils.py                # Utility functions for analysis
├── run_var_model.py        # Complete walkthrough script
├── README.md               # This file
└── Output/
    ├── forecast_24month.csv     # Generated forecasts
    └── model_summary.txt        # Model diagnostics
```

## Getting Started

### Prerequisites

```bash
pip install pandas numpy statsmodels scipy scikit-learn openpyxl
```

### Quick Start

```bash
cd VAR
python run_var_model.py
```

This executes the complete workflow:
1. ✓ Load and prepare economic data
2. ✓ Examine data characteristics
3. ✓ Select optimal lag order
4. ✓ Fit VAR model
5. ✓ Review model diagnostics
6. ✓ Generate 24-month forecast
7. ✓ Analyze and save results

## File Descriptions

### `data_preparation.py`

**Purpose**: Transform raw CSV data into VAR-ready variables

**Key Functions**:
- `load_data()` - Load raw CSV file
- `calculate_gdp_growth()` - Monthly GDP % change
- `calculate_cpi_change()` - Monthly inflation rate
- `calculate_yield_spread()` - 10yr - 3mo yield difference
- `prepare_var_data()` - Combines all above + handles missing values

**Example Usage**:
```python
from data_preparation import prepare_var_data

var_data, original_df = prepare_var_data("../dataocean.csv", verbose=True)
print(var_data.head())
```

### `var_model.py`

**Purpose**: Build, fit, and use VAR models

**Key Classes**:
- `VARModelBuilder` - Main class for VAR modeling

**Main Methods**:
- `select_optimal_lag(maxlags=12)` - Find best lag order using AIC/BIC/FPE/HQIC
- `fit_model(lag_order)` - Fit VAR with specified lags
- `forecast(steps=24)` - Generate forecasts
- `get_model_diagnostics()` - Return key statistics
- `get_impulse_response(periods=10)` - Shock analysis
- `get_forecast_error_variance_decomposition()` - Variance contribution

**Example Usage**:
```python
from var_model import VARModelBuilder
from data_preparation import prepare_var_data

# Prepare data
var_data, _ = prepare_var_data("../dataocean.csv")

# Build model
model = VARModelBuilder(var_data)
model.select_optimal_lag(maxlags=12)
model.fit_model()

# Forecast
forecast_24m = model.forecast(steps=24)
print(forecast_24m)
```

### `utils.py`

**Purpose**: Utility functions for advanced analysis

**Key Functions**:
- `save_model()` / `load_model()` - Persist fitted models
- `multi_step_forecast()` - Forecasts at multiple horizons
- `compare_scenarios()` - Scenario analysis
- `calculate_forecast_confidence_intervals()` - Forecast bounds
- `create_forecast_summary_table()` - Quarterly aggregation
- `export_forecast_to_excel()` - Export to Excel

### `run_var_model.py`

**Purpose**: Complete walkthrough demonstrating entire workflow

Prints detailed explanations at each step and saves results to:
- `forecast_24month.csv` - Raw forecast values
- `model_summary.txt` - Model equations and summary

## Understanding the Workflow

### Step 1: Data Preparation

Raw data is transformed into three standardized variables:

**GDP Growth**:
```
gdp_growth[t] = ((GDP[t] - GDP[t-1]) / GDP[t-1]) * 100
```

**CPI Change**:
```
cpi_change[t] = ((CPI[t] - CPI[t-1]) / CPI[t-1]) * 100
```

**Yield Spread**:
```
yield_spread[t] = rate_10yr[t] - rate_3mo[t]
```

### Step 2: Lag Selection

Tests different lag orders (1-12 months) and compares:

- **AIC** (Akaike): Trade-off between fit and complexity
- **BIC** (Bayesian): Conservative, penalizes complexity more
- **FPE** (Forecast Prediction Error): Focuses on forecast accuracy
- **HQIC** (Hannan-Quinn): Alternative criterion

The most frequently recommended lag across criteria is selected.

### Step 3: Model Fitting

Estimates parameters for the VAR system:
- Each variable regressed on its own lags + all other variable lags
- Parameters capture temporal and cross-variable relationships
- Model diagnostics assess overall quality

### Step 4: Forecasting

Uses fitted model to project:
- Current state of the system
- Estimated relationships between variables
- Time evolution forward 24 months

### Step 5: Analysis

Examine:
- Point forecasts (expected values)
- Uncertainty measures (standard errors)
- Consistency with historical patterns
- Economic plausibility

## Interpreting Results

### Forecast Output

CSV file contains columns:
- `gdp_growth` - Expected monthly GDP growth rate (%)
- `cpi_change` - Expected monthly inflation (%)
- `yield_spread` - Expected 10yr-3mo yield difference (bps)

### Key Metrics

**Descriptive Statistics**:
```
count     24.000000
mean       0.125000  <- Average monthly forecast value
std        0.042516  <- Forecast volatility
min       -0.015000  <- Most pessimistic forecast
max        0.285000  <- Most optimistic forecast
```

**Model Quality**:
- **Lower AIC/BIC** = Better model fit
- **Higher Log-Likelihood** = Better overall fit
- **FPE** = Out-of-sample forecast error estimate

## Advanced Usage

### Scenario Analysis

Compare forecasts under different economic assumptions:

```python
from utils import compare_scenarios

scenarios = {
    'high_inflation': {'cpi_change': 0.5},
    'recession': {'gdp_growth': -0.5},
    'yield_inversion': {'yield_spread': -1.0}
}

results = compare_scenarios(var_data, scenarios, model)
```

### Multi-Horizon Forecasts

Generate forecasts at multiple time horizons:

```python
from utils import multi_step_forecast

forecasts = multi_step_forecast(model, steps_list=[12, 24, 36])

for horizon, forecast in forecasts.items():
    print(f"\n{horizon}-Month Forecast:")
    print(forecast)
```

### Confidence Intervals

Calculate forecast uncertainty bounds:

```python
from utils import calculate_forecast_confidence_intervals

point_forecast, lower, upper = calculate_forecast_confidence_intervals(
    model, steps=24, confidence=0.95
)

print(f"95% Confidence Intervals:")
print(f"Lower: {lower}")
print(f"Point: {point_forecast}")
print(f"Upper: {upper}")
```

## Model Diagnostics Explained

### Residual Analysis

The `model.results.resid` contains model residuals:
- Should be approximately normally distributed
- Should have no autocorrelation (checked via Ljung-Box test)
- Should be contemporaneously correlated (expected in VAR)

### Information Criteria

Lower values indicate better models:

| Criterion | Formula | Interpretation |
|-----------|---------|-----------------|
| AIC | 2k - 2ln(L) | Tends to select more parameters |
| BIC | k·ln(n) - 2ln(L) | More conservative than AIC |
| FPE | exp((k/n)·ln(Σ)) | Focuses on forecast accuracy |
| HQIC | 2k·ln(ln(n)) - 2ln(L) | Balance between AIC and BIC |

Where:
- k = number of parameters
- n = number of observations  
- L = log-likelihood
- Σ = residual covariance determinant

## Common Issues and Solutions

### Issue: Model Won't Converge

**Causes**: Too many lags, near-multicollinearity, or data quality issues

**Solutions**:
- Reduce `maxlags` in `select_optimal_lag()`
- Verify data quality and check for missing values
- Standardize variables using z-scores

### Issue: Forecast Seems Unrealistic

**Causes**: Insufficient observations, structural break in data, or regime change

**Solutions**:
- Use more recent subset of data if structural break suspected
- Check historical data against actual values
- Consider rolling window estimation

### Issue: High Forecast Uncertainty

**Causes**: High data volatility or weak relationships between variables

**Solutions**:
- Consider longer forecast horizons with wider confidence bands
- Add exogenous variables if available
- Use restricted VAR models with economic constraints

## Extending the Model

### Adding More Variables

```python
# Modify data_preparation.py to include more variables
# Then pass to VARModelBuilder with custom column names

model = VARModelBuilder(
    var_data,
    variable_columns=['gdp_growth', 'cpi_change', 'yield_spread', 'unemployment_rate']
)
```

### Structural VAR (SVAR)

For causal interpretation of shocks, implement SVAR:
- Imposes economic theory constraints
- Identifies structural shocks vs. noise
- Requires additional assumptions

### Bayesian VAR

For uncertain parameter values:
- Uses prior distributions
- Particularly useful with limited data
- Implemented via `BayesianVAR` in statsmodels

## References

### Key Papers

- Sims, C. A. (1980). "Macroeconomics and Reality". Econometrica 48(1): 1-48
- Stock, J. H., & Watson, M. W. (2001). "Vector Autoregressions"
- Lütkepohl, H. (2005). "New Introduction to Multiple Time Series Analysis"

### Python Documentation

- [statsmodels VAR](https://www.statsmodels.org/stable/tsa_api.html)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [NumPy Guide](https://numpy.org/doc/)

## License

This code is provided as-is for educational and research purposes.

## Contact & Support

For questions or issues:
1. Check the docstrings in each module
2. Review example usage in `run_var_model.py`
3. Examine output files for diagnostic information

## Version History

- v1.0 (2024): Initial release
  - Basic VAR model implementation
  - Lag selection via information criteria
  - 24-month forecasting
  - Utility functions for analysis

---

**Last Updated**: 2024

**Status**: Active Development

**Next Steps**:
- [ ] Add visualization functions
- [ ] Implement Bayesian VAR
- [ ] Add structural identification
- [ ] Create web interface for model
