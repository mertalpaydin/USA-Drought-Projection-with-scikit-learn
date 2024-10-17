import pandas as pd


def ee_array_to_df(arr, list_of_bands, region, id_num):
    """
    Transforms ee.Image.getRegion.getInfo() object to pandas.DataFrame.

    :param arr: ee.Image.getRegion.getInfo() object to be transformed.
    :param list_of_bands: list of bands to be extracted from arr.
    :param region: 'Name' of the region for which the data is to be extracted.
    :param id_num: unique identifier for each region.

    :return: A pandas DataFrame containing lists of bands extracted from ee.Image.getRegion.getInfo() object, region
        name, id_num and image extraction date.
    """
    df = pd.DataFrame(arr)
    band_list = list_of_bands[:]

    # Rearrange the header.
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)

    # Remove rows without data inside.
    df = df[['time', *band_list]].dropna(ignore_index=True)

    # Convert the data to numeric values and take monthly means
    for band in band_list:
        df[band] = pd.to_numeric(df[band], errors='coerce')
        # Calculate min and max on top mean since the climate data includes min and max humidity instead of mean
        if band == "huss":
            df["huss_min"] = df[band].min()
            df["huss_max"] = df[band].max()
            band_list.extend(["huss_min", "huss_max"])
        df[band] = df[band].mean()

    # Add region and id columns
    df['region'] = pd.Series([str(region) for _ in range(len(df.index))])
    df['id'] = pd.Series([str(id_num) for _ in range(len(df.index))])

    # Keep the columns of interest.
    df = df[["id", "region", 'time', *band_list]]

    return df[:1]
