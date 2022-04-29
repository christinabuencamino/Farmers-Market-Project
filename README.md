# Does The Presence Of A Farmer's Market In A Zip Code Predict Resident Median Income?

**Name**: Christina Buencamino<br>
**Email**: christina.buencamino28@myhunter.cuny.edu | c.buencamino123@gmail.com <br>
**Resources**: Please see bottom of page.<br>
**Abstract**: My final project aims to discover if there is a correlation between the median income of a NYC zip code and if a farmer's market shows up in said zip code. I used an OpenData CSV breakdown of NYC farmer's markets present in 2019, along with census data that shows the 2019 median income (in dollars) of zip codes in NYC.
<br>
[Github](https://github.com/christinabuencamino) | [LinkedIn](https://www.linkedin.com/in/christina-buencamino/)
<br>
## Initial Hypothesis & Notes
My initial hypothesis was that farmer's markets target higher income neighborhoods. My reasoning for this was mainly from personal experience, since the markets I have been to in NYC have had some pretty steep prices.<br>
Additionally, I would like to disclose that I had to edit the farmer's market csv on lines 34 and 64 because the inputted coordinates were not accurate, so I replaced them with their respective coordinates as found on Google Maps.
<br>
## Common Functions
Throughout my code blocks, there are references to functions that were defined to help build/clean up the data used so it could be analyzed in a cleaner way. Here are their definitions:<br>

```python
'''
Helper function to call geolocator for calculating farmer's market zip codes.
gis.stackexchange.com/questions/352961/convert-lat-lon-to-zip-postal-code-using-python
'''
def get_zipcode(df, geolocator, lat, lon):
    location = geolocator.reverse((df[lat], df[lon]))
    return location.raw['address']['postcode']

'''
Generates series of farmer's market zipcodes using geopy's Nominatim
'''
def GenerateZipCode():
    locator = geopy.Nominatim(user_agent='my-project-for-DS-3')
    cols_kept = ['Borough', 'Market Name', 'Street Address', 'Latitude', 'Longitude']
    markets = pd.read_csv("DOHMH_Farmers_Markets.csv", usecols=cols_kept)

    markets_1 = markets.iloc[:50,:]
    zipcodes_1 = markets_1.apply(get_zipcode, axis=1, geolocator=locator, 
        lat='Latitude', lon='Longitude')
    zipcodes_1 = zipcodes_1.replace('112321', '11232')

    markets_2 = markets.iloc[50:100,:]
    zipcodes_2 = markets_2.apply(get_zipcode, axis=1, geolocator=locator, 
        lat='Latitude', lon='Longitude')

    markets_3 = markets.iloc[100:,:]
    zipcodes_3 = markets_3.apply(get_zipcode, axis=1, geolocator=locator, 
        lat='Latitude', lon='Longitude')

    zipcodes = zipcodes_1.append(zipcodes_2)
    zipcodes = zipcodes.append(zipcodes_3)

    zipcodes.name = 'Market_Present'

    return zipcodes


'''
Calls zip code and median_data functions and merges them together to create complete 
dataframe for analysis.
'''
def CombineMedianMarket():
    # Call function to generate zip codes for markets
    zipcodes = GenerateZipCode()
    zipcodes = zipcodes.astype(int)

    # Clean up median income csv
    median_data = CreateMedianData()

    # Merge market data and median income data, and isolate only zip codes that have markets
    combined_df = median_data.merge(zipcodes, left_on='NAME', right_on='Market_Present', how='left')
    combined_df.Market_Present = combined_df.Market_Present.notnull().astype(int)
    combined_df = combined_df.sort_values(by=['S1903_C03_001E'])
    combined_df = combined_df[combined_df['S1903_C03_001E'] != 0]



    return combined_df


'''
Cleans up Median income csv to only include zip code and 2019 median income per 
zipcode, while fixing data types.
'''
def CreateMedianData():
    # Read in csv and clean up data
    median_data = pd.read_csv('MedianIncome.csv', usecols=['NAME', 'S1903_C03_001E'])
    median_data = median_data.dropna()
    median_data = median_data.drop([0]) # Drop row of column headers
    median_data['NAME'] = [re.sub(r'ZCTA5 ', '', str(x)) for x in median_data['NAME']] # Reformat zip codes
    median_data['NAME'] = median_data['NAME'].astype('int')
    median_data['S1903_C03_001E'] = median_data['S1903_C03_001E'].replace("-", "0")
    median_data['S1903_C03_001E'] = median_data['S1903_C03_001E'].replace("250,000+", "250000")
    median_data['S1903_C03_001E'] = median_data['S1903_C03_001E'].astype('float')

    return median_data

```


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
    folium.TileLayer('cartodbpositron').add_to(m) 
    
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
    folium.TileLayer('cartodbpositron').add_to(m) 
    m.choropleth(geo_data='ZipCodeGeo.json', fill_color='YlGnBu', fill_opacity=0.9, line_opacity=0.5,
                 data=medianData,
                 threshold_scale = [0, 10276, 41775, 89075, 170050, 215950, 250001],
                 key_on='feature.properties.postalCode',
                 columns=['NAME', 'S1903_C03_001E'],
                 nan_fill_color='white',
                 legend_name='Median Income')
```

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

Looking at this map, I was unable to see a clear trend in the data, so I moved on to other means of data analysis.
<br>
## Graphing The Data
I wanted to look at a more general breakdown of the distribution of markets across NYC in order to see if there is a correlation purely from that. To begin this process, I made a bar plot of markets per borough, as seen below.
<br>

![https://user-images.githubusercontent.com/66935005/165559362-b55e017d-56e9-4b7d-bfa3-f44f57d2511c.png](https://user-images.githubusercontent.com/66935005/165559362-b55e017d-56e9-4b7d-bfa3-f44f57d2511c.png)


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
Coupling this with the [U.S. Census Bureau's median income facts per borough](https://www.census.gov/quickfacts/fact/table/queenscountynewyork,newyorkcountynewyork,bronxcountynewyork,kingscountynewyork,richmondcountynewyork/HSG010219), this bar plot does not support my original hypothesis, and rather supports the notion that farmer's markets target the middle class. Manhattan and Staten Island have the highest incomes, and while Manhattan has the second highest amount of Farmer's Markets, Staten Island has the least by a very large amount. Even if we were to not include Staten Island (due to just how few markets there are versus zip code), the next borough with the most amount of markets is the Bronx, which has the lowest income in comparison to the other boroughs.

<br>While this does not support my original hypothesis, I must look deeper at individual zipcodes since every borough has zipcodes that range in median incomes, so the placement of these market's is important. 
<br><br>
To visualize the distribution of markets in specific zip codes, I categorized the data into federal income tax brackets to see if there was an obvious distribution:<br>

![https://user-images.githubusercontent.com/66935005/165646579-32deb3e2-63f9-4708-a414-3e27a2784d01.png](https://user-images.githubusercontent.com/66935005/165646579-32deb3e2-63f9-4708-a414-3e27a2784d01.png)


```python
def GenerateTaxPlot():
    # Call function to generate zip codes for markets
    zipcodes = GenerateZipCode()
    zipcodes = zipcodes.astype(int)

    # Clean up median income csv
    medianData = pd.read_csv('MedianIncome.csv', usecols=['NAME', 'S1903_C03_001E'])
    medianData = medianData.dropna()
    medianData = medianData.drop([0])
    medianData['NAME'] = [re.sub(r'ZCTA5 ', '', str(x)) for x in medianData['NAME']]
    medianData['NAME'] = medianData['NAME'].astype('int')
    medianData['S1903_C03_001E'] = medianData['S1903_C03_001E'].replace("-", "0")
    medianData['S1903_C03_001E'] = medianData['S1903_C03_001E'].replace("250,000+", "250000")
    medianData['S1903_C03_001E'] = medianData['S1903_C03_001E'].astype('float')

    # Merge market data and median income data, and isolate only zip codes that have markets
    graph_data = medianData.merge(zipcodes, left_on='NAME', right_on='Market_Present', how='left')
    graph_data.Market_Present = graph_data.Market_Present.notnull().astype(int)
    graph_data = graph_data.sort_values(by=['S1903_C03_001E'])
    graph_data = graph_data[graph_data['Market_Present'] == 1]
    graph_data = graph_data[graph_data['S1903_C03_001E'] != 0]

    # Categorize data into tax brackets
    taxes = [0, 10276, 41775, 89075, 170050, 215950, 250001]
    labels = ['$0 - $10276', '$10276 - $41775', '$41775 - $89075', '$89075 - $170050', '$170050 - $215950', '215950+']
    graph_data['Tax_Bracket'] = pd.cut(graph_data['S1903_C03_001E'], taxes, labels=labels, ordered=False)

    # Fix indexing
    brackets = graph_data['Tax_Bracket'].value_counts().to_frame()
    brackets = brackets.reindex(labels)

    # Create bar plot
    fig, ax = plt.subplots()
    sns.barplot(x=brackets.index, y=brackets['Tax_Bracket'], data=brackets,
                             color="salmon")
    plt.xticks(rotation=30)
    ax.set_xlabel('Tax Brackets')
    ax.set_ylabel('Number of Farmers Markets')
    ax.set_title("Number Of Markets Per Zip Code's Tax Bracket In NYC")
```
<br>
From this graph, we can see that farmer's markets tend to target the second and third brackets the most, placing a majority of them between roughly $10,000 - $90,000 median income zip codes. This makes sense, since a majority of the zip codes in New York City belong to these two brackets. To confirm this, I proceeded to make a double bar histogram to compare the amount of zip codes and farmer's markets per tax bracket:
<br>

![https://user-images.githubusercontent.com/66935005/165875235-70179c9d-cc1b-4de9-b010-d746e3590ed0.png](https://user-images.githubusercontent.com/66935005/165875235-70179c9d-cc1b-4de9-b010-d746e3590ed0.png)

<br>
As we can see, a majority of these zip codes are encompassed in these two brackets, which offsets the data. It would be unfair to draw the conclusion that farmer's markets "target" certain income zones, since the distribution of zip codes by tax bracket is heavily skewed.
<br>
## Model Prediction
**Note**: Unfortunately, due to the nature of my data and the time constraint, I was unable to find a method of data prediction that fit the data well, since my data is essentially a boolean of whether or not a market was present in a zip code (aka largely categorical). However, after much discussion (thanks Susan!) and research, there were other ways I could attempt to analyze my data, as seen below. If I had more time (and I intend to update this project once I have time), I would read up on other methods of prediction not discussed in class. I would also definitely broaden my data so I would have more to work with, and thus more to analyze.
<br>
To begin, I ran a logistic regression on the data and plotted the results. From my research and what we've learned in class, this seemed to be the most logical approach since I could treat the presence of a market as a boolean, thus making it a dependent variable that fits for logistic regression:<br>

![https://user-images.githubusercontent.com/66935005/165962954-1d582155-7550-4c81-ba70-57c5360dc391.png](https://user-images.githubusercontent.com/66935005/165962954-1d582155-7550-4c81-ba70-57c5360dc391.png)

```python
def LogRegAndConfMatrix():
    combined_df = pd.read_csv("out.csv")  # saved the combined df to not overload geopy + save time

    X = combined_df[['S1903_C03_001E']]
    y = combined_df['Market_Present'].to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42)

    lr = LogisticRegression()
    lr.fit(X_train, y_train)

    # print(lr.score(X_test, y_test))

    y_pred = lr.predict(X_test)

    p = sns.lmplot(
        x='S1903_C03_001E', y='Market_Present',
        data=combined_df,
        fit_reg=False, ci=False,
        y_jitter=0.01,
        scatter_kws={'alpha': 0.3},
        palette='flare',

    )
    p = (p.set_axis_labels("Median Income Per NYC Zip Code", "Market Present"))
    xs = np.linspace(-2, 250002, 100)
    ys = lr.predict_proba(xs.reshape(-1, 1))[:, 1]
    plt.plot(xs, ys)
    plt.title("Logistic Regression Of Median Income Versus Market Present")
    plt.show()
```


Due to the small size of the data, there was not a lot for the model to work with and it could not create a good prediction. There is a very slight negative prediction, to the point where it could be negligible. As seen below, it is not very accurate either:<br>

```python
    y_pred = lr.predict(X_test)
    print('Accuracy of logistic regression: {:.2f}'.format(lr.score(X_test, y_test)))
    
    # Prints: Accuracy of logistic regression: 0.53
```


The confusion matrix that is produced from this analysis is as follows:<br>

![https://user-images.githubusercontent.com/66935005/166070505-64b67e09-d1be-4c6f-bb8d-72be3f2f9e03.png](https://user-images.githubusercontent.com/66935005/166070505-64b67e09-d1be-4c6f-bb8d-72be3f2f9e03.png)

```python
    ax = sns.heatmap(cm, annot=True, cmap='Blues')

    ax.set_title('Confusion Matrix\n\n')
    ax.set_xlabel('\nPredicted Values')
    ax.set_ylabel('Actual Values ')

    ax.xaxis.set_ticklabels(['False', 'True'])
    ax.yaxis.set_ticklabels(['False', 'True'])

    plt.show()
```
<br>
With this model, there is not much to conclude besides that this model does not fit the data well. The confusion matrix shows almost an even split between correctly guessed predictions versus incorrect, which goes along with the 53% accuracy rate. 

## Final Thoughts
I wouldn't necessarily claim that there's a "perfect" predictive model for this data - rather, the data requires other numerical categories and the perspective of this project needs to be adjusted. There are too many clashing variables that get in the way of accurate predictive modeling, such as the skew towards the middle tax bracket, the make up of NYC, the low number of farmer's markets compared to the number of zipcodes, and the lack of overall data categories. Even when I tried to split the data in other ways (middle class versus not middle class, for example), I did not notice any noteworthy changes in the calculations. 
<br><br>
When I come back to this project, I intend to reframe my original question in order to include numerical data, such as "does the median income of a zip code predict the _revenue_ of a farmer's market", or different methods of analyzing how the populations of these zip codes interact with the farmer's markets (depending on the data sets online, of course). This definitely helped me understand how important figuring out the scope of your data and research question is when developing a project.

## Resources
**Market data**: https://data.cityofnewyork.us/dataset/DOHMH-Farmers-Markets/8vwk-6iz2/data<br>
**GeoJSON data**: https://data.beta.nyc/dataset/nyc-zip-code-tabulation-areas/resource/6df127b1-6d04-4bb7-b983-07402a2c3f90<br>
    https://github.com/fedhere/PUI2015_EC/blob/master/mam1612_EC/nyc-zip-code-tabulation-areas-polygons.geojson<br>
**GeoJSON help**: https://stjohn.github.io/teaching/seminar4/s17/cw6.html<br>
**Folium help**: https://medium.com/@meganlyons_79212/creating-maps-with-folium-baa6ff0f5c44<br>
    https://levelup.gitconnected.com/visualizing-housing-data-with-folium-maps-4718ed3452c2<br>
    https://medium.com/@saidakbarp/interactive-map-visualization-with-folium-in-python-2e95544d8d9b<br>
    https://towardsdatascience.com/visualizing-data-at-the-zip-code-level-with-folium-d07ac983db20<br>
    https://medium.com/datadream/mapping-with-folium-a-tale-of-3-cities-8e5ab7f4e53d<br>
    https://github.com/python-visualization/folium/issues/1404<br>
**Geopy help**: https://www.geeksforgeeks.org/get-zip-code-with-given-location-using-geopy-in-python/<br>
**Credit for zip code help**: https://gis.stackexchange.com/questions/352961/convert-lat-lon-to-zip-postal-code-using-python<br>
**Regex help**: https://stackoverflow.com/questions/53962844/applying-regex-across-entire-column-of-a-dataframe<br>
**Pandas**: https://groups.google.com/g/pyqtgraph/c/trmr_5dV6Uc?pli=1<br>
**Logistic Reg**: http://www.textbook.ds100.org/ch/24/classification_log_reg.html<br>
Data science textbook<br>

## Thank you for reading!!

