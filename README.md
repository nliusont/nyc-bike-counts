# nyc-bike-counts

This repo cleans NYC bike count data and weather data and trains an xgboost model to predict daily bike ridership. This repo supports two Streamlit data apps:
* [NYC Bike Counts](https://nyc-bike-counts.streamlit.app/)
  * [Repo](https://github.com/nliusont/nyc-bike-counts-app)
* [NYC Bike Prediction](https://nyc-bike-prediction.streamlit.app/)
  * [Repo](https://github.com/nliusont/nyc-bike-prediction)

## Notebooks
### et.ipynb
This notebook takes in bike counts and bike counter csvs and performs the following:
* trims the bike counters to the predominant counters and removes duplicative counters
* links together the two Kent Ave counters
* slices off anomalous data that occurs after counter installation
* groups by by hour and week for visualization
* creates display data for streamlit app

### make_dataset_w_features.ipynb
This notebook totals the bike counts for the most predominant bike counters then pulls in weather data to be used as input features for modelling.
There two weather sources for data, though it could all be retrieved from Open Mateo (which was discovered later in the project)

### predict_counts.ipynb
This notebook takes the output of make_dataset_w_feature.ipynb and trains an xgboost regressor model
