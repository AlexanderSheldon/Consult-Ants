import pandas as pd
import numpy as np
import datetime as dt

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
yield_df = yield_df[yield_df['date'].dt.day == 1]
yield_df['date'] = yield_df["date"].dt.strftime("%Y-%m")

big_df = pd.merge(CPI_df, yield_df, on='date', how='inner')
print(big_df.head())



big_df.to_csv('dataocean.csv')