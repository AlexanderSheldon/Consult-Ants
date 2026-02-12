import pandas as pd
import numpy as np
import datetime as dt
from openpyxl import load_workbook

CPI_df = pd.read_csv("Datasets/CPIAUCSL.csv")
ebp_df = pd.read_csv("Datasets/ebp_csv.csv")
yield_df = pd.read_csv("Datasets/par-yield-curve-rates-1990-2023.csv")

# print(CPI_df.head())
# print(ebp_df.head())
# print(yield_df.head())

"""------------------------------------------------------------------------
Create Month and year vars
------------------------------------------------------------------------"""

CPI_df['date'] = pd.to_datetime(CPI_df["observation_date"]).dt.strftime("%Y-%m")

yield_df['date'] = pd.to_datetime(yield_df['date'])
# Take the first observation available in each month
yield_df['year_month'] = yield_df['date'].dt.to_period('M')
yield_df = yield_df.sort_values('date').groupby('year_month', as_index=False).first()
# Set date to first of month for consistency
yield_df['date'] = yield_df['year_month'].dt.to_timestamp()
yield_df = yield_df.drop('year_month', axis=1)
yield_df['date'] = yield_df['date'].dt.strftime("%Y-%m")

# GDP
GDP_df = pd.read_excel("Datasets/US-Monthly-GDP-History-Data-Dec2025.xlsx", sheet_name='Data')
GDP_df['date'] = pd.to_datetime(GDP_df.iloc[:, 0]).dt.strftime("%Y-%m")

# UNRate
UN_df = pd.read_csv("Datasets/UNRATE.csv")
UN_df['date'] = pd.to_datetime(UN_df['observation_date']).dt.strftime("%Y-%m")

"""------------------------------------------------------------------------
Merge Data
------------------------------------------------------------------------"""


big_df = pd.merge(CPI_df, yield_df, on='date', how='right', suffixes=('_cpi', '_yield'))


big_df = big_df.sort_values('date', ascending=True)

big_df = pd.merge(big_df, GDP_df, on='date', how='right')

big_df = pd.merge(big_df, UN_df, on='date', how='right')

# Filter data to 1992-01 through 2023-12
big_df = big_df[(big_df['date'] >= '1992-01') & (big_df['date'] <= '2023-12')]

print(big_df.head())

big_df.to_csv('dataocean.csv')