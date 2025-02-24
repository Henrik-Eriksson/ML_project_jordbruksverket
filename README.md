# ML_project_jordbruksverket

All parameters for SMHI weather
| Parameter | Title                           | Summary                                                  | Unit                    |
|-----------|---------------------------------|----------------------------------------------------------|-------------------------|
| 21        | Gust Wind                       | Maximum, once per hour                                   | meters per second       |
| 39        | Dew Point Temperature           | Instantaneous value, once per hour                        | Celsius                 |
| 11        | Global Irradiance (Swedish stations) | 1‑hour average, every hour                           | watts per square meter  |
| 22        | Air Temperature                 | Average, once per month                                   | Celsius                 |
| 26        | Air Temperature                 | Minimum, twice per day at 06:00 and 18:00                 | Celsius                 |
| 27        | Air Temperature                 | Maximum, twice per day at 06:00 and 18:00                 | Celsius                 |
| 19        | Air Temperature                 | Minimum, once per day                                     | Celsius                 |
| 1         | Air Temperature                 | Instantaneous value, once per hour                        | Celsius                 |
| 2         | Air Temperature                 | Daily average, once per day at 00:00                      | Celsius                 |
| 20        | Air Temperature                 | Maximum, once per day                                     | Celsius                 |
| 9         | Air Pressure Reduced to Sea Level | At sea level, instantaneous value, once per hour         | hectopascal             |
| 24        | Longwave Irradiance             | 1‑hour average, every hour                                | watts per square meter  |
| 40        | Ground Condition                | Instantaneous value, once per day at 06:00                 | Code                    |
| 25        | Maximum of Average Wind Speed   | Maximum of 10‑min averages over 3 hours, once per hour    | meters per second       |
| 28        | Cloud Base                      | Lowest cloud layer, instantaneous value, once per hour     | meters                  |
| 30        | Cloud Base                      | Second cloud layer, instantaneous value, once per hour     | meters                  |
| 32        | Cloud Base                      | Third cloud layer, instantaneous value, once per hour      | meters                  |
| 34        | Cloud Base                      | Fourth cloud layer, instantaneous value, once per hour     | meters                  |
| 36        | Cloud Base                      | Lowest cloud base, instantaneous value, once per hour      | meters                  |
| 37        | Cloud Base                      | Lowest cloud base, minimum over 15 minutes, once per hour  | meters                  |
| 29        | Cloud Amount                    | Lowest cloud layer, instantaneous value, once per hour     | Code                    |
| 31        | Cloud Amount                    | Second cloud layer, instantaneous value, once per hour     | Code                    |
| 33        | Cloud Amount                    | Third cloud layer, instantaneous value, once per hour      | Code                    |
| 35        | Cloud Amount                    | Fourth cloud layer, instantaneous value, once per hour     | Code                    |
| 17        | Precipitation                   | Twice daily, at 06:00 and 18:00                           | Code                    |
| 18        | Precipitation                   | Once daily, at 18:00                                      | Code                    |
| 15        | Precipitation Intensity         | Maximum over 15 minutes, 4 times per hour                  | millimeters per second  |
| 38        | Precipitation Intensity         | Maximum of averages over 15 minutes, 4 times per hour      | millimeters per second  |
| 23        | Precipitation Amount            | Total, once per month                                     | millimeters             |
| 14        | Precipitation Amount            | Total over 15 minutes, 4 times per hour                    | millimeters             |
| 5         | Precipitation Amount            | Total for 1 day, once per day at 06:00                     | millimeters             |
| 7         | Precipitation Amount            | Total for 1 hour, once per hour                            | millimeters             |
| 6         | Relative Humidity               | Instantaneous value, once per hour                         | Percent                 |
| 13        | Present Weather                 | Instantaneous value, once per hour or 8 times per day      | Code                    |
| 12        | Visibility                      | Instantaneous value, once per hour                         | meters                  |
| 8         | Snow Depth                      | Instantaneous value, once per day at 06:00                 | meters                  |
| 10        | Sunshine Duration               | Total for 1 hour, once per hour                            | Seconds                 |
| 16        | Total Cloud Cover               | Instantaneous value, once per hour                         | Percent                 |
| 4         | Wind Speed                      | 10‑minute average, once per hour                           | meters per second       |
| 3         | Wind Direction                  | 10‑minute average, once per hour                           | Degrees                 |


Exploratory Analysis

This shows that they don't have many records for the northern part of sweden, And It might be reasonable to disregard those records and the weather data for that part of sweden
Län (County)
![image](https://github.com/user-attachments/assets/f4046c96-9f34-4976-b3e5-882cd5a5f42c)
Delområde (More Specific Part of County)
![image](https://github.com/user-attachments/assets/a47e7383-ea6c-4d19-8a8b-9034e1704fdc)


Some crops we can disregards entirely because there isn't a lot of data for us to work with
![image](https://github.com/user-attachments/assets/1f78137a-60bc-4b45-ba07-2f3e0c4fb2b8)


Most common pest
![image](https://github.com/user-attachments/assets/210d248b-22b0-47e1-8cb8-ec9ad1ce808b)

see heatmap html for interactive
![image](https://github.com/user-attachments/assets/88a27948-2f38-4ae1-a100-ed0d6965d983)


Composite graph for all counts of pests for each crop
https://github.com/Henrik-Eriksson/ML_project_jordbruksverket/blob/main/composite_groda_skadegorare_grid_sorted.html
