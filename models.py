import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv("dataocean.csv")

# Prepare data
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

# Extract CPI and drop NaN values
cpi_data = df[['date', 'CPIAUCSL']].dropna()
cpi_data.set_index('date', inplace=True)

print("CPI Data Shape:", cpi_data.shape)
print("\nFirst few rows:")
print(cpi_data.head())

# Test for stationarity
def adf_test(series, name=''):
    result = adfuller(series.dropna())
    print(f'\nADF Test for {name}:')
    print(f'ADF Statistic: {result[0]:.6f}')
    print(f'p-value: {result[1]:.6f}')
    print(f'Critical Values: {result[4]}')
    if result[1] <= 0.05:
        print(f"✓ {name} is stationary")
        return True
    else:
        print(f"✗ {name} is non-stationary (needs differencing)")
        return False

# Check stationarity
is_stationary = adf_test(cpi_data['CPIAUCSL'], 'Original CPI')

# If not stationary, difference the data
if not is_stationary:
    cpi_diff = cpi_data['CPIAUCSL'].diff().dropna()
    adf_test(cpi_diff, 'Differenced CPI')

# Split data into train/test (80/20)
train_size = int(len(cpi_data) * 0.8)
train_data = cpi_data[:train_size]
test_data = cpi_data[train_size:]

print(f"\nTrain size: {len(train_data)}, Test size: {len(test_data)}")

# Fit SARIMA model
# (p,d,q)(P,D,Q,s) - adjust these parameters based on your ACF/PACF plots
# Common starting point: (1,1,1)(1,1,1,12) for monthly data
try:
    print("\n" + "="*50)
    print("Fitting SARIMA model...")
    print("="*50)
    
    model = SARIMAX(
        train_data['CPIAUCSL'],
        order=(1, 1, 1),           # (p,d,q) - AR, differencing, MA
        seasonal_order=(1, 1, 1, 12),  # (P,D,Q,s) - seasonal components, 12 for monthly
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    
    results = model.fit(disp=False)
    print(results.summary())
    
    # Make predictions on test set
    predictions = results.get_forecast(steps=len(test_data))
    pred_df = predictions.conf_int()
    pred_df['predictions'] = predictions.predicted_mean
    
    # Calculate metrics
    rmse = np.sqrt(mean_squared_error(test_data['CPIAUCSL'], pred_df['predictions']))
    mae = mean_absolute_error(test_data['CPIAUCSL'], pred_df['predictions'])
    
    print(f"\n" + "="*50)
    print("Model Performance on Test Set:")
    print("="*50)
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    
    # Future forecast (next 12 months)
    print(f"\n" + "="*50)
    print("Forecasting next 12 months...")
    print("="*50)
    
    future_forecast = results.get_forecast(steps=12)
    future_df = future_forecast.conf_int()
    future_df['forecast'] = future_forecast.predicted_mean
    print(future_df)
    
    # Plot results
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot training data
    ax.plot(train_data.index, train_data['CPIAUCSL'], label='Training Data', color='blue')
    
    # Plot test data
    ax.plot(test_data.index, test_data['CPIAUCSL'], label='Actual Test Data', color='green')
    
    # Plot predictions
    ax.plot(test_data.index, pred_df['predictions'], label='Predictions', color='red', linestyle='--')
    
    # Add confidence intervals
    ax.fill_between(test_data.index,
                    pred_df.iloc[:, 0],
                    pred_df.iloc[:, 1],
                    alpha=0.3, color='red')
    
    ax.set_xlabel('Date')
    ax.set_ylabel('CPI')
    ax.set_title('SARIMA CPI Forecast')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('cpi_forecast.png', dpi=100)
    print("\n✓ Plot saved as 'cpi_forecast.png'")
    
except Exception as e:
    print(f"Error fitting model: {e}")
    print("\nTry adjusting the SARIMA parameters (p,d,q,P,D,Q,s)")



