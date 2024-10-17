import ee
import json
import pandas as pd
import os
from date_ranges import get_month_ranges
from img_array_to_df import ee_array_to_df

# geojson file containing the geometric info of the region of interest
path = "us-climate-regions_corrected.geojson"

with open(path) as json_data:
    regions_json = json.load(json_data)
    json_data.close()

ee.Authenticate()
ee.Initialize(project="ee-mertalpaydin91")

# images will be extracted initially with the smallest scale possible and in case of an error,
# extraction will be retried with a larger scale
scale_range = [2000, 5000, 7500, 10000]


# for which dates data will be extracted
initial_date = "2010-01-01"
final_date = "2023-12-31"

# get the first dates for each month in the data range.
# images will be extracted for a month to reduce image size
initial_dates, final_dates = get_month_ranges(initial_date, final_date)

# dict of databases and list of bands to be extracted from each

database_dict = {
    "GRIDMET/DROUGHT": ["pdsi"],
    "IDAHO_EPSCOR/TERRACLIMATE": ["soil", "vs"],
    "MODIS/061/MOD13A2": ["NDVI"],
    "IDAHO_EPSCOR/GRIDMET": ["pr", "tmmn", "tmmx", "rmin", "rmax"],
    "NASA/GDDP-CMIP6": ["pr", "tasmin", "tasmax", "huss", "sfcWind"]
}

for database in database_dict.keys():

    # data range for the climate forcast data will be different
    if database == "NASA/GDDP-CMIP6":
        initial_date = "2024-01-01"
        final_date = "2050-12-31"

        initial_dates, final_dates = get_month_ranges(initial_date, final_date)

    data_band = database_dict[database]
    df_cols = data_band.copy()
    df = pd.DataFrame(columns=df_cols.extend(["id", "region", "time"]))

    # extract image for each month in the specified range
    for index in range(len(initial_dates)):

        i_date, f_date = initial_dates[index], final_dates[index]

        # since ee image for prediction data includes different models,
        # model and scenario name are added as additional filters
        if database == "NASA/GDDP-CMIP6":
            data_image = (ee.ImageCollection(database).
                          select(data_band).
                          filterDate(i_date, f_date).
                          filter(ee.Filter.eq('model', 'GISS-E2-1-G')).
                          filter(ee.Filter.eq('scenario', 'ssp245')))
        else:
            data_image = (ee.ImageCollection(database).
                          select(data_band).
                          filterDate(i_date, f_date))

        # get geometry of each region from the geojson data and convert it to ee geometry
        for feature in regions_json["features"]:
            region = ee.Geometry.MultiPolygon(feature["geometry"]["coordinates"])

            # try extracting info for the given region with the smallest possible scale
            # if no error, break the loop. otherwise try with a larger scale
            for scale in scale_range:
                try:
                    pixel_info_points = data_image.getRegion(geometry=region, scale=scale).getInfo()
                    ee_df = ee_array_to_df(
                        pixel_info_points,
                        data_band,
                        feature["properties"]["NAME"],  # name of the region
                        feature["properties"]["CLIMDIV_ID"]  # unique id of the region
                    )
                except ee.ee_exception.EEException:
                    pass

                if not ee_df.empty:
                    break

            df = pd.concat([df, ee_df], ignore_index=True)

        print(f"{database} {i_date[5:7]}/{i_date[:4]} Done")

        # after completing extraction for each year, save the data to a csv file to avoid data loss
        if (index + 1) % 12 == 0:
            directory = f"{os.path.abspath(os.getcwd())}/csv"
            file_name = (os.path.join(directory,
                                      f"us_climate_data_{database.replace('/', '_')}_{i_date[:4]}.csv")
                         .replace("\\", "/"))
            if not os.path.isdir(directory):
                os.mkdir(directory)
            df.to_csv(file_name, index=False)
            print(f"output complete: {file_name}")
            df = df[0:0]
            # reconnect to ee in order to assure data extraction continuous
            ee.Authenticate()
            ee.Initialize(project="ee-mertalpaydin91")
