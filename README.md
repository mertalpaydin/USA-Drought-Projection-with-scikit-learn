# USA Drought Projection with Scikit-Learn

This project is developed as a course project for the **Introduction to Data Analytics in Business** taught in 2024 fall Semester.

The dataset used in the project is extracted from the *Google Earth Engine* using 5 different databases as a source. Python code for the dataset extraction can be found in the Github repository. 4 of the aforementioned databases are used to extract past climate data (from Jan, 2010 to Dec, 2023). The fifth database, *NASA/GDDP-CMIP6* is used to extract NASA's climate predictions from 2024 to 2050.

We have utilized a US Climate Regions geojson file provided by *data.gov* for data extraction. All extracted data were either monthly aggregated or aggregated by the our code.

Our aim is to predict the **Palmer Drought Severity Index**(PDSI), using more than 20 different features, either directly extracted from the Earth Engine or articulated by the code below. Some of the features available in the original dataset are dropped due to Nasa predictions not including them. 

Columns in the unaltered database are as follow:

- **PDSI** (target variable): Palmer Drought Severity Index (scale from -4 or less extreme drought to 4 or more extremely wet).
- **id** (not a feature): Unique id of the climate region.
- **region** (not a feature): Name of the climate region.
- **time** (not a feature): Time of the first observation.
- **key** (not a feature): Unique id made up of id_year_of_observation_month_of_observation. Used as an index.
- **pr**: Daily average precipitation amount in milimeters
- **tmmm**: Maximum temperature in Celsius
- **tmmx**: Maximum temperature in Celsius
- **tmean**: Average of tmmn and tmmx
- **rmin**: Minimum relative humidity(%)
- **rmax**: Maximum relative humidity(%)
- **vs** (not a feature): Wind-speed at 10m in m/s
- **soil** (not a feature): Soil moisture, derived using a one-dimensional soil water balance model in milimeters
- **NDVI** (not a feature): 16-day NDVI(Normalized Difference Vegetation Index) average

We've tested 5 different models with different parameters through Randomized Search Cross Validation. SVM(kernel=rbf) provided the best model for our project. Data for the years from 2011 to 2021 are treated as a training set, whereas data for the years 2022 and 2023 are selected as a test set.

As a last step, we have utilized Nasa climate predictions to predict PDSI in 2050.

For more detailed information please refer to the project presentation and/or report or contact the repository owner.
