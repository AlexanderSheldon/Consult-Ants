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
yield_df = yield_df[yield_df['date'].dt.day == 1]
yield_df['date'] = yield_df["date"].dt.strftime("%Y-%m")

# Housing combos
h1 = pd.read_csv("HousingDev/COMPU1UNSA.csv")
h2 = pd.read_csv("HousingDev/COMPU5MUNSA.csv")
h3 = pd.read_csv("HousingDev/COMPU24UNSA.csv")
h4 = pd.read_csv("HousingDev/COMPUTNSA.csv")

hs = [h1,h2,h3,h4]
for h in hs:
    h['date'] = pd.to_datetime(h["observation_date"]).dt.strftime("%Y-%m")
    h.drop('observation_date', axis=1, inplace=True)

# GDP
GDP_df = pd.read_excel("Datasets/US-Monthly-GDP-History-Data-Dec2025.xlsx", sheet_name='Data')
GDP_df['date'] = pd.to_datetime(GDP_df.iloc[:, 0]).dt.strftime("%Y-%m")

"""------------------------------------------------------------------------
Merge Data
------------------------------------------------------------------------"""


big_df = pd.merge(CPI_df, yield_df, on='date', how='right', suffixes=('_cpi', '_yield'))

for h in hs:
    big_df = pd.merge(big_df, h, on='date', how='right', suffixes=('', '_housing'))

big_df = big_df.sort_values('date', ascending=True)

big_df = pd.merge(big_df, GDP_df, on='date', how='right')

print(big_df.head())

big_df.to_csv('dataocean.csv')