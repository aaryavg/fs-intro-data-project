# Step 1
import polars as p1

path = "data/software-data.parquet"

# Reading and loading the binary parquet file which consists of raw binary data into a Polars DataFrame
df = p1.read_parquet(path)

#Load and forward fill the the empty cells, then backfill leading nulls, which also carries previous sensor readings forward across time gaps and cleans leading nulls
df = df.fill_null(strategy="forward").fill_null(strategy="backward")

#Print column names and the first 20 rows
print("Column in file:")
print(df.columns)
print("\nFirst 20 rows:")
print(df.head(20))

# Step 2: Calculate Ground Speed & Graphs vs. Time
import numpy as np
import matplotlib.pyplot as plt

#Phyics Constants
WR = 0.2 # Wheel Radius
GR = 12/41 #Sprocket Gear Ratio

#Speed_ms column Adding w/ Polars
df = df.with_columns(
    (pl.col("SME_TRQSPD_Speed") * GR * (2 * np.pi / 60) * WR).alias("Speed_ms")
)


