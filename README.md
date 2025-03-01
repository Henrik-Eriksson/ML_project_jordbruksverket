# ML_project_jordbruksverket



We are utilizing weather data from the (Global Forecast System) which is a weather prediction model predicting as much as 16 days ahead.
Three resolutions available: **0.25 deg**, 0.5 deg, 1 deg.
![image](https://github.com/user-attachments/assets/62e60369-7f8a-4f9f-a55a-dbce8b3298c7)



We are currently fetching and looking at the 0.25 deg model has data available from 2015-present.
[Fetched from here](https://rda.ucar.edu/datasets/d084001/)
Look at the google colab [Jupyter Notebook](https://colab.research.google.com/drive/1Ahj0wkcGkgYc-S7XyKM-uBMObADCJct8?usp=sharing) on how we are fetching this data.

## Running Instructions

Before working with the data in the repository and/or using the heatmap tool, It is necessary as a first time to download all required packages and the data itself which is located on google drive, We have made a simple script for this, Which assumes python 3+ and pip is already installed

### Setup
Open a command prompt in the working directory of the project
```
py setup.py
```
This will install all required packages and download jordbruksverkets data which we have fetched in advance from their API

### To use the heatmap tool (for analysis purposeses)
Go to exploratory_analysis/heatmap
```
py main.py
```
This will generate a static HTML file which you can open in your browser


## Exploratory Analysis

This shows that they don't have many records for the northern part of sweden, And It might be reasonable to disregard those records and the weather data for that part of sweden
Län (County)
![image](https://github.com/user-attachments/assets/f4046c96-9f34-4976-b3e5-882cd5a5f42c)
Delområde (More Specific Part of County)
![image](https://github.com/user-attachments/assets/a47e7383-ea6c-4d19-8a8b-9034e1704fdc)

Some crops we can disregards entirely because there isn't a lot of data for us to work with
![image](https://github.com/user-attachments/assets/1f78137a-60bc-4b45-ba07-2f3e0c4fb2b8)

Most common pest
![image](https://github.com/user-attachments/assets/210d248b-22b0-47e1-8cb8-ec9ad1ce808b)

See the exploratory_analysis/heatmap tool for a more interactive view


![image](https://github.com/user-attachments/assets/88a27948-2f38-4ae1-a100-ed0d6965d983)
