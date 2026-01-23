import pandas as pd
import numpy as np

CPI_df = pd.read_csv("Datasets/CPIAUCSL.csv")
ebp_df = pd.read_csv("Datasets/ebp_csv.csv")
yield_df = pd.read_csv("Datasets/par-yield-curve-rates-1990-2023.csv")

print(CPI_df.head())
print(ebp_df.head())
print(yield_df.head())

np.corrcoef(CPI_df['CPIAUCSL'], )