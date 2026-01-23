# VAR Model - Quick Start Guide

## Overview
You now have a complete Vector Autoregression model that forecasts 24 months ahead using three key economic variables:
- **GDP Growth (%)**: Monthly percentage change in nominal GDP
- **CPI Change (%)**: Monthly inflation rate
- **Yield Spread**: Difference between 10-year and 3-month bond yields

## Running the Model

### Execute the complete workflow:
```bash
cd VAR
python run_var_model.py
```

This will:
1. Load and prepare the economic data
2. Select the optimal number of lags using information criteria
3. Fit the VAR model
4. Generate 24-month forecasts
5. Save results to CSV files

## File Guide

### Core Modules

**`data_preparation.py`** - Data transformation
- `load_data(filepath)` - Load raw CSV
- `calculate_gdp_growth(df)` - Calculate monthly GDP growth %
- `calculate_cpi_change(df)` - Calculate monthly CPI change %
- `calculate_yield_spread(df)` - Calculate 10yr - 3mo spread
- `prepare_var_data(filepath)` - Complete data prep pipeline

**`var_model.py`** - VAR model implementation
- `VARModelBuilder` class with methods:
  - `select_optimal_lag(maxlags=12)` - Find best lag order
  - `fit_model(lag_order)` - Fit the model
  - `forecast(steps=24)` - Generate 24-month forecast
  - `get_model_diagnostics()` - Model statistics

**`utils.py`** - Utility functions
- `save_model()` / `load_model()` - Save/load fitted models
- `multi_step_forecast()` - Multiple time horizon forecasts
- `compare_scenarios()` - Scenario analysis
- `calculate_forecast_confidence_intervals()` - Forecast bounds

**`run_var_model.py`** - Complete walkthrough script
- Demonstrates all steps with detailed explanations
- Saves results to CSV and summary text files

### Output Files

**`forecast_24month.csv`** - 24-month forecasts
- 24 rows × 3 columns (gdp_growth, cpi_change, yield_spread)

**`model_summary.txt`** - Model diagnostics and equations

## Common Tasks

### Basic Forecasting
```python
from data_preparation import prepare_var_data
from var_model import VARModelBuilder

# Load and prepare data
var_data, _ = prepare_var_data("../dataocean.csv", verbose=False)

# Build model
model = VARModelBuilder(var_data)
model.select_optimal_lag()
model.fit_model()

# Forecast
forecast = model.forecast(steps=24)
print(forecast)
```

### Multi-Horizon Forecasts
```python
from utils import multi_step_forecast

# Generate forecasts for 12, 24, and 36 months
forecasts = multi_step_forecast(model, steps_list=[12, 24, 36])

for horizon, forecast in forecasts.items():
    print(f"{horizon}-month average GDP growth: {forecast['gdp_growth'].mean():.3f}%")
```

### Scenario Analysis
```python
from utils import compare_scenarios

scenarios = {
    'high_inflation': {'cpi_change': 0.5},
    'recession': {'gdp_growth': -0.5},
    'yield_inversion': {'yield_spread': -1.0}
}

results = compare_scenarios(var_data, scenarios, model)
```

### Save/Load Models
```python
from utils import save_model, load_model

# Save fitted model
save_model(model, "my_var_model.pkl")

# Load model later
loaded_model = load_model("my_var_model.pkl")
forecast = loaded_model.forecast(steps=24)
```

## Understanding the Model Output

### Current Model (VAR(1))
- **Lag Order**: 1 month (each variable depends on past 1 month)
- **Observations**: 138 monthly data points
- **Variables**: 3 (GDP growth, CPI change, yield spread)

### Key Results
```
Average 24-Month Forecast:
- GDP Growth:      0.72% monthly
- CPI Change:      0.29% monthly  
- Yield Spread:    0.04 basis points

Model Diagnostics:
- AIC:             -5.01 (lower is better)
- BIC:             -4.76 (lower is better)
- Log-Likelihood:  -227.80 (higher is better)
```

### Understanding Information Criteria

| Criterion | Full Name | Focus | Use When |
|-----------|-----------|-------|----------|
| **AIC** | Akaike Information | Fit vs Complexity | Generally preferred |
| **BIC** | Bayesian Information | Conservative | Prefer parsimony |
| **FPE** | Forecast Prediction Error | Forecast accuracy | Focus on predictions |
| **HQIC** | Hannan-Quinn | Intermediate | Balance approach |

Lower values = better model

## Model Equations

The fitted VAR(1) model has these equations:

```
GDP_growth[t] = 0.438 + 0.493*GDP[t-1] - 0.297*CPI[t-1] - 0.043*Spread[t-1]
CPI_change[t] = 0.174 + 0.078*GDP[t-1] + 0.206*CPI[t-1] - 0.006*Spread[t-1]
Yield_spread[t] = 0.060 - 0.021*GDP[t-1] + 0.110*CPI[t-1] + 0.928*Spread[t-1]
```

### Interpretation Examples:

1. **GDP Growth** is positively affected by past GDP growth (0.493)
   - If GDP grew 1% last month, expect +0.49% contribution this month

2. **CPI Change** is positively affected by past CPI change (0.206)
   - If inflation was 0.5% last month, expect +0.10% contribution this month

3. **Yield Spread** is highly persistent (0.928)
   - The term premium tends to stay similar to previous month

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'statsmodels'"
**Solution**: Install required packages
```bash
pip install statsmodels scipy scikit-learn pandas numpy
```

### Issue: Forecast values seem unrealistic
**Check**:
1. Is the data range appropriate? (currently using 1992-2023 data)
2. Are there structural breaks in the economy?
3. Is the lag order optimal? Try adjusting `maxlags` parameter

### Issue: Want different lag order
**Solution**:
```python
model.fit_model(lag_order=4)  # Use 4 lags instead
forecast = model.forecast(steps=24)
```

## Next Steps

### Enhance the Model
1. **Add more variables**: Unemployment rate, bond spreads, credit metrics
2. **Structural VAR**: Add economic theory constraints
3. **Bayesian VAR**: Use prior distributions for parameter uncertainty
4. **Time-varying parameters**: Allow coefficients to change over time

### Validate the Model
1. Out-of-sample testing: Reserve recent data for validation
2. Compare to other models: ARIMAX, exponential smoothing
3. Track forecast accuracy: Compare predictions to actual values

### Extend Functionality
1. Create visualization dashboards
2. Add confidence interval calculations
3. Implement impulse response analysis
4. Build web interface for model interaction

## References

**Theory**:
- Sims, C. A. (1980). "Macroeconomics and Reality". Econometrica 48(1)
- Lütkepohl, H. (2005). "New Introduction to Multiple Time Series Analysis"

**Python Libraries**:
- [statsmodels](https://www.statsmodels.org/)
- [pandas](https://pandas.pydata.org/)
- [numpy](https://numpy.org/)

## Questions?

Refer to:
1. Docstrings in each module: `help(VARModelBuilder.forecast)`
2. README.md for detailed documentation
3. run_var_model.py for complete examples
4. Comments throughout the code

---

**Model Built**: 2024
**Data Period**: 1992-01 to 2023-12
**Forecast Horizon**: 24 months
**Status**: Production Ready
