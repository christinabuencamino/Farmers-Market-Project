# Can Farmer's Markets Predict The Median Income Of A Zip Code?

**Name**: Christina Buencamino<br>
**Email**: christina.buencamino28@myhunter.cuny.edu (school) | c.buencamino123@gmail.com (work)<br>
**Resources**: Please see bottom of page.<br>
**Abstract**: My final project aims to discover if there is a correlation between the median income of a zip code and how many (if any) farmer's markets station in said zip code. I used an OpenData CSV breakdown of NYC farmer's markets present in 2019, along with census data that shows the 2019 median income (in dollars) of zip codes in NYC.<br>
<br>
**URL**: https://christinabuencamino.github.io/Farmers-Market-Project/<br>
**GitHub**: christinabuencamino<br>
**LinkedIn**: christina-buencamino<br>
<br>
## Initial Hypothesis
My initial hypothesis was that farmer's markets target higher income neighborhoods. My reasoning for this was mainly from personal experience, since the markets I have been to in NYC have had some pretty steep prices.
<br>
## Mapping The Data
To begin, I created a map of all of the farmer's markets in NYC using the <a href url="https://data.cityofnewyork.us/dataset/DOHMH-Farmers-Markets/8vwk-6iz2/data">DOHMH Farmers Markets Open Data set</a>.

![Farmers-Market-Locations](https://user-images.githubusercontent.com/66935005/164956393-2ecf082a-17a7-4ed8-b624-539d243b601f.png)


```python
def CreateFarmersMap(csv):
    # Read in coordinates from csv
    cols_kept = ['Latitude', 'Longitude']
    markets = pd.read_csv(csv, usecols=cols_kept)
    
    # Create map
    m = folium.Map(location=[40.74, -73.96356241384754], zoom_start=11.5)
    folium.TileLayer('stamentoner').add_to(m) # black and white filter
    
    # Cycle through coordinates and create markets
    for lat, lon in zip(markets['Latitude'], markets['Longitude']):
        folium.CircleMarker([lat, lon], radius=3, color='blue', fill=True, fill_color='blue', fill_opacity=0.7).add_to(m)
```
Next, I created a chloropleth map of the ranges of median incomes in NYC using the <a href url="https://data.census.gov/cedsci/table?q=Income%20%28Households,%20Families,%20Individuals%29&g=1600000US3651000%248600000&y=2019&tid=ACSST5Y2019.S1903">2019 census data</a> and <a href url="https://github.com/fedhere/PUI2015_EC/blob/master/mam1612_EC/nyc-zip-code-tabulation-areas-polygons.geojson">NYC geojson data</a>.

![Median-Choropleth-Map](https://user-images.githubusercontent.com/66935005/164957410-6f065888-5daa-4716-96f1-b49c1f2ddb96.png)
<br><br>
![Median-Choropleth-Legend](https://user-images.githubusercontent.com/66935005/164957415-d13c6ee8-694f-4535-8b68-ff53877f35b0.png)

```python
def CreateMedianChoropleth():
    # Read in csv and clean up data
    medianData = pd.read_csv('MedianIncome.csv', usecols=['NAME', 'S1903_C03_001E'])
    medianData = medianData.dropna()
    medianData = medianData.drop([0]) # Drop row of column headers
    medianData['NAME'] = [re.sub(r'ZCTA5 ', '', str(x)) for x in medianData['NAME']] # Reformat zip codes
    medianData['NAME'] = medianData['NAME'].astype('str')
    medianData['S1903_C03_001E'] = medianData['S1903_C03_001E'].replace("-", "0")
    medianData['S1903_C03_001E'] = medianData['S1903_C03_001E'].replace("250,000+", "250000")
    medianData['S1903_C03_001E'] = medianData['S1903_C03_001E'].astype('float')

    # Create map using geojson data boundaries to connect with zip codes from csv, and coloring based on income
    m = folium.Map(location=[40.75, -74], zoom_start=11.4)
    folium.TileLayer('stamentoner').add_to(m) # Black and white filter
    m.choropleth(geo_data='ZipCodeGeo.json',
                        fill_color='Reds', fill_opacity=0.9, line_opacity=0.5,
                        data=medianData,
                        key_on='feature.properties.postalCode',
                        columns=['NAME', 'S1903_C03_001E'],
                        legend_name='Median Income')
```

Finally, I combined both maps in order ot visually see the breakdown of farmer's market location versus median income.

![Median-Market-Map](https://user-images.githubusercontent.com/66935005/164957710-0b202d63-440d-47c3-af42-8a625e65ace1.png)
<br><br>
![Median-Choropleth-Legend](https://user-images.githubusercontent.com/66935005/164957415-d13c6ee8-694f-4535-8b68-ff53877f35b0.png)

```python
    # Read in csv and clean up data
    medianData = pd.read_csv('MedianIncome.csv', usecols=['NAME', 'S1903_C03_001E'])
    medianData = medianData.dropna()
    medianData = medianData.drop([0])
    medianData['NAME'] = [re.sub(r'ZCTA5 ', '', str(x)) for x in medianData['NAME']]
    medianData['NAME'] = medianData['NAME'].astype('str')
    medianData['S1903_C03_001E'] = medianData['S1903_C03_001E'].replace("-", "0")
    medianData['S1903_C03_001E'] = medianData['S1903_C03_001E'].replace("250,000+", "250000")
    medianData['S1903_C03_001E'] = medianData['S1903_C03_001E'].astype('float')

    # Create map, now with choropleth shading and also market markers
    m = folium.Map(location=[40.75, -74], zoom_start=11.4)
    folium.TileLayer('stamentoner').add_to(m)
    m.choropleth(geo_data='ZipCodeGeo.json',
                        fill_color='Reds', fill_opacity=0.9, line_opacity=0.5,
                        data=medianData,
                        key_on='feature.properties.postalCode',
                        columns=['NAME', 'S1903_C03_001E'],
                        legend_name='Median Income')

    cols_kept = ['Latitude', 'Longitude']
    markets = pd.read_csv('DOHMH_Farmers_Markets.csv', usecols=cols_kept)

    for i in range(0, len(markets)):
        folium.CircleMarker(
            [markets.iloc[i]['Latitude'], markets.iloc[i]['Longitude']], 
            radius=3, 
            color='blue', 
            fill=True, 
            fill_color='blue', 
            fill_opacity=0.7
        ).add_to(m)
```
<br>
Looking at this map, I was unable to see a clear trend in the data, so I moved on to other means of data analysis.
<br>
## Graphing The Data
insert smart stuff from my big brain here when i am not sleep deprived
