import os
import pandas as pd
from datetime import datetime


def process_csv_files(directory, folder_name):
    """
    Function to combine all csv files in a given folder
    """
    # List to store DataFrames from each CSV file
    dfs = []

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)

            # Read CSV file
            df = pd.read_csv(file_path)

            # Convert 'time' column from Unix timestamp to datetime
            df['time'] = pd.to_datetime(df['time'], unit="ms")

            # Create 'key' column by merging 'id' and 'time'
            def key_create(row):
                # return f"{row['id']}_{str(row['time'])[:4]}_{str(row['time'])[5:7]}"
                return f"{row['id']}_{row['time'].year}_{str(row['time'].month).zfill(2)}"

            df["key"] = df.apply(key_create, axis="columns")

            # scaling and unit conversions as stated by database documentations
            if folder_name == "IDAHO_EPSCOR_GRIDMET":
                # convert K to Celsius and create mean temp and mean humidity columns
                df["tmmn"] = df["tmmn"] - 273.15
                df["tmmx"] = df["tmmx"] - 273.15
                df["tmean"] = df.apply(lambda row: (row["tmmn"] + row["tmmx"]) / 2, axis="columns")
                df["rmean"] = df.apply(lambda row: (row["rmin"] + row["rmax"]) / 2, axis="columns")

            elif folder_name == "IDAHO_EPSCOR_TERRACLIMATE":
                # scaling
                df["soil"] = df["soil"] * 0.1
                df["vs"] = df['vs'] * 0.1

            elif folder_name == "MODIS_061_MOD13A2":
                # scaling
                df["NDVI"] = df['NDVI'] * 0.0001

            elif folder_name == "NASA_GDDP-CMIP6":
                # convert K to Celsius create mean temp column
                df["tasmin"] = df['tasmin'] - 273.15
                df["tasmax"] = df['tasmax'] - 273.15
                df["tasmean"] = df.apply(lambda row: (row["tasmin"] + row["tasmax"]) / 2, axis="columns")
                # convert precipitation rate from kg/m^2/s per day to mm per day
                df["pr"] = df['pr'] * 86400
                # convert humidity to a percent
                df["huss_min"] = df['huss_min'] * 100
                df["huss_max"] = df['huss_max'] * 100
                # rename columns so that they match climate data
                df.rename(columns={
                    "tasmin": "tmmn",
                    "tasmax": "tmmx",
                    "tasmean": "tmean",
                    "huss_min": "rmin",
                    "huss_max": "rmax",
                    "sfcWind": "vs"
                }, inplace=True)
                df.drop(columns=["huss"], inplace=True)
            dfs.append(df)

    # Concatenate all DataFrames from the directory
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return None


# working directory where directories storing csv files are located
current_path = "C:/Users/merta/OneDrive/Desktop/FS Courses/Data Analytics/Drought_Projection/project_files/csv"

# List to store DataFrames from each directory
climate_dfs = []
prediction_df = None

# Iterate through all directories under the current path
for directory in os.listdir(current_path):
    dir_path = os.path.join(current_path, directory)
    if os.path.isdir(dir_path):
        df = process_csv_files(dir_path, directory)
        if df is not None:
            # Predictions will not be combined with the climate data, stored in a separate df.
            if directory != "NASA_GDDP-CMIP6":
                climate_dfs.append(df)
            else:
                prediction_df = df

# Join all DataFrames using the 'key' column (Applies on to the climate_data as they come from different sources)
if len(climate_dfs) > 1:
    final_df = climate_dfs[0]
    for df in climate_dfs[1:]:
        final_df = final_df.merge(df, on="key", how='outer', suffixes=(None, "__"))
        final_df.drop(columns=["id__", "region__", "time__"], inplace=True)
elif len(climate_dfs) == 1:
    final_df = climate_dfs[0]
else:
    print("No CSV files found in any directory.")
    final_df = None

# Save the final DataFrames to a CSV files
if final_df is not None:
    file_name = (os.path.join(current_path, f"climate_data_combined.csv"))
    final_df.to_csv(file_name, index=False)
    print("Combined data saved to 'climate_data_combined.csv'")

if prediction_df is not None:
    file_name = (os.path.join(current_path, f"prediction_data_combined.csv"))
    prediction_df.to_csv(file_name, index=False)
    print("Combined data saved to 'prediction_data_combined.csv'")
