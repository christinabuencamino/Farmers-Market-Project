# Can Farmer's Markets Predict The Median Income Of A Zip Code?

**Name**: Christina Buencamino<br>
**Email**: christina.buencamino28@myhunter.cuny.edu | c.buencamino123@gmail.com (work)<br>
**Resources**: Please see bottom of page.<br>
**Abstract**: My final project aims to discover if there is a correlation between the median income of a zip code and how many (if any) farmer's markets station in said zip code. I used an OpenData CSV breakdown of NYC farmer's markets present in 2019, along with census data that shows the 2019 median income (in dollars) of zip codes in NYC.<br>
<br>
[Github](https://github.com/christinabuencamino)
<br>
[LinkedIn](https://www.linkedin.com/in/christina-buencamino/)
<br>
## Initial Hypothesis & Notes
My initial hypothesis was that farmer's markets target higher income neighborhoods. My reasoning for this was mainly from personal experience, since the markets I have been to in NYC have had some pretty steep prices.
Additionally, I would like to disclose that I had to edit the farmer's market csv on lines 34 and 64 because the inputted coordinates were not accurate, so I replaced them with their respective coordinates as found on Google Maps.
<br>
## Mapping The Data
To begin, I created a map of all of the farmer's markets in NYC using the [DOHMH Farmers Markets Open Data set](https://data.cityofnewyork.us/dataset/DOHMH-Farmers-Markets/8vwk-6iz2/data).

<iframe src="Market-Map.html" height="800" width="650"></iframe>

```python
def CreateFarmersMap(csv):
    # Read in coordinates from csv
    cols_kept = ['Latitude', 'Longitude']
    markets = pd.read_csv(csv, usecols=cols_kept)
    
    # Create map
    m = folium.Map(location=[40.74, -73.96356241384754], zoom_start=11.5)
    folium.TileLayer('stamentoner').add_to(m) # black and white filter
    
    # Create NYC zip code borders from geojson data
    m.choropleth(geo_data='ZipCodeGeo.json', line_color='black',
               line_weight=1, fill_color='transparent')
    
    # Cycle through coordinates and create markets
    for i in range(0, len(markets)):
        folium.Marker(
            location=[markets.iloc[i]['Latitude'], markets.iloc[i]['Longitude']],
            icon=BeautifyIcon(
                icon='star',
                inner_icon_style='color:lightgreen;font-size:10px;',
                background_color='transparent',
                border_color='transparent')
        ).add_to(m)
```
Next, I created a chloropleth map of the ranges of median incomes in NYC using the [2019 census data](https://data.census.gov/cedsci/table?q=Income%20%28Households,%20Families,%20Individuals%29&g=1600000US3651000%248600000&y=2019&tid=ACSST5Y2019.S1903) and [NYC geojson data](https://github.com/fedhere/PUI2015_EC/blob/master/mam1612_EC/nyc-zip-code-tabulation-areas-polygons.geojson). Note that completely white areas within NYC imply that there was no census data on that zip code (an example being Central Park in Manhattan). I scaled the map by [federal income tax brackets](https://www.nerdwallet.com/article/taxes/federal-income-tax-brackets).

<iframe src="Median-Map.html" height="800" width="650"></iframe>

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
    folium.TileLayer('cartodbpositron').add_to(m)  # Black and white filter
    m.choropleth(geo_data='ZipCodeGeo.json', fill_color='YlGnBu', fill_opacity=0.9, line_opacity=0.5,
                 data=medianData,
                 threshold_scale = [0, 10276, 41775, 89075, 170050, 215950, 250001],
                 key_on='feature.properties.postalCode',
                 columns=['NAME', 'S1903_C03_001E'],
                 nan_fill_color='white',
                 legend_name='Median Income')
```
<br>

Finally, I combined both maps in order to visually see the breakdown of farmer's market location versus median income.<br>

<iframe src="Median-Market-Map.html" height="800" width="650"></iframe>


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
    folium.TileLayer('cartodbpositron').add_to(m)
    m.choropleth(geo_data='ZipCodeGeo.json',
                        fill_color='YlGnBu', fill_opacity=0.9, line_opacity=0.5,
                        data=medianData,
                        key_on='feature.properties.postalCode',
                        columns=['NAME', 'S1903_C03_001E'],
                        legend_name='Median Income')

    cols_kept = ['Latitude', 'Longitude']
    markets = pd.read_csv('DOHMH_Farmers_Markets.csv', usecols=cols_kept)

    for i in range(0, len(markets)):
        folium.Marker(
            location=[markets.iloc[i]['Latitude'], markets.iloc[i]['Longitude']],
            icon=BeautifyIcon(
                icon='star',
                inner_icon_style='color:yellow;font-size:9px;',
                background_color='transparent',
                border_color='transparent')
        ).add_to(m)
```
<br>
Looking at this map, I was unable to see a clear trend in the data, so I moved on to other means of data analysis.
<br>
## Graphing The Data
I wanted to look at a more general breakdown of the distribution of markets across NYC in order to see if there is a correlation purely from that. To begin this process, I made a bar plot of markets per borough, as seen below.
<br>

![Borough_Bar_Plot](https://user-images.githubusercontent.com/66935005/165559362-b55e017d-56e9-4b7d-bfa3-f44f57d2511c.png)


```python
def GenerateBarPlot(market_csv):
    # Cleanup farmer's market csv
    market = pd.read_csv(market_csv)
    market = market['Borough'].value_counts().reset_index(inplace=False)  # Create dataframe of each borough and their count of markets
    market.columns = ["Borough", "Number of Farmer's Markets"]
    boroughs = market
    
    # Generate bar plot
    f, ax = plt.subplots(figsize=(6, 15))
    sns.set_color_codes("pastel")
    ax.grid(color='black', axis='x', ls='-', lw=0.25)
    ax.set_axisbelow(True)
    sns.barplot(x="Number of Farmer's Markets", y="Borough", data=boroughs,
                label="Farmer's Markets Present", color="salmon")
    ax.set(xlim=(0, 50), ylabel="Borough",
           xlabel="Number Of Farmer's Markets")

    plt.title("Number Of Farmer's Markets Per Borough")
    plt.show()
```
<br>
Coupling this with the [U.S. Census Bureau's median income facts per borough](https://www.census.gov/quickfacts/fact/table/queenscountynewyork,newyorkcountynewyork,bronxcountynewyork,kingscountynewyork,richmondcountynewyork/HSG010219), this bar plot shows that there is not a strong correlation between the location of a farmer's market and borough income. Manhattan and Staten Island have the highest incomes, and while Manhattan has the second highest amount of Farmer's Markets, Staten Island has the least by a very large amount. Even if we were to not include Staten Island**, the next borough with the most amount of markets is the Bronx, which has the lowest income in comparison to the other boroughs. While this does not support my original hypothesis, I must look deeper at individual zipcodes since every borough has zipcodes that range in median incomes, so the placement of these market's is important.
<br><br>
** I would like to note that Staten Island is a powerful outlier, and therefore I will be making observations with and without it. As a native Staten Islander, I understand that Staten Island has a large disconnect from the rest of NYC, so trends that exist in the other four boroughs may not apply to Staten Island due to large transportation, distance, and environmental differences. However, it is still a borough, so of course I will be including it in my research!
<br>
## Model Prediction
Predicting my specific data is not as straightforward since it is simply location based. If I had more time, I would read up on Time Series forecasting and other methods of prediction not focused on in class, so that I could find a model that truly fits my data. In the mean time, however, I attempted to use Logistic Regression in order to make predictions, since I can treat the presence of a farmer's market as a boolean value. Logistic Regression supports boolean prediction, so let's go from there.
<br><br>
First I made a regular plot of my data. The curve shows there is more markets in the lower tax brackets.<br>

![Reg_Plot](https://user-images.githubusercontent.com/66935005/165627627-4bf2e26a-0363-4645-9033-88da9f7921b5.png)
