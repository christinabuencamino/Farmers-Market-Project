# Does The Presence Of A Farmer's Market In A Zip Code Predict Resident Median Income?

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
Coupling this with the [U.S. Census Bureau's median income facts per borough](https://www.census.gov/quickfacts/fact/table/queenscountynewyork,newyorkcountynewyork,bronxcountynewyork,kingscountynewyork,richmondcountynewyork/HSG010219), this bar plot shows that there is not a strong correlation between the location of a farmer's market and borough income. Manhattan and Staten Island have the highest incomes, and while Manhattan has the second highest amount of Farmer's Markets, Staten Island has the least by a very large amount. Even if we were to not include Staten Island, the next borough with the most amount of markets is the Bronx, which has the lowest income in comparison to the other boroughs. While this does not support my original hypothesis, I must look deeper at individual zipcodes since every borough has zipcodes that range in median incomes, so the placement of these market's is important.
<br><br>
To visualize the distribution of markets in specific zip codes, I categorized the data into federal income tax brackets to see if there was an obvious distribution:<br>

![Tax_Brackets](https://user-images.githubusercontent.com/66935005/165646579-32deb3e2-63f9-4708-a414-3e27a2784d01.png)


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
From this graph, we can see that farmer's markets tend to target the second and third brackets the most, placing a majority of them between roughly $10,000 - $90,000 median income zip codes. However, this cannot be accepted as the final result, since there are more zip codes that fall into this range than out of it, thus increasing the probability of a market ending up here. Because of this, I proceeded to make a double bar histogram to compare the amount of zip codes and farmer's markets per tax bracket:
<br>

![DoubleBar](https://user-images.githubusercontent.com/66935005/165875235-70179c9d-cc1b-4de9-b010-d746e3590ed0.png)

<br>
As we can see, the amount of zip codes located in the central tax bracket is overwhelming compared to the other zip codes. Therefore, it would be unfair to claim that the markets target a specific income based off of NYC data. To try to gain a better perspective, I moved on to predicive modeling.
<br>
## Model Prediction
Note: Unfortunately, due to the nature of my data and the amount of time I had to complete this project, I was unable to find a method of data prediction that fit the data well, since my data is essentially a boolean of whether or not a market was present in a zip code (aka largely categorical). However, after much discussion (thanks Susan!) and research, there were other ways I could analyze my data, as seen below. If I had more time (and I intend to update this project once I have time), I would read up on other methods of prediction not discussed in class, such as Time Series forecasting which was recommended to me. I would also consider broadening my data so I would have more to work with. 
<br>
To begin, I ran a logistic regression on the data and plotted the results. From my research and what we've learned in class, this was the most logical approach since I could treat the presence of a market as a boolean, thus making it a dependent variable that fits for logistic regression:<br>

![LogReg](https://user-images.githubusercontent.com/66935005/165962954-1d582155-7550-4c81-ba70-57c5360dc391.png)

```python
def LogReg():
    combined_df = CombineMedianMarket()

    X = combined_df[['S1903_C03_001E']].to_numpy()
    y = combined_df['Market_Present'].to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=66, random_state=42)

    lr = LogisticRegression()
    lr.fit(X_train, y_train)

    p = sns.lmplot(
        x='S1903_C03_001E', y='Market_Present',
        data=combined_df,
        fit_reg=False, ci=False,
        y_jitter=0.01,
        scatter_kws={'alpha':0.3},
        palette='flare',

    )
    p = (p.set_axis_labels("Median Income Per NYC Zip Code", "Market Present"))
    xs = np.linspace(-2, 250002, 100)
    ys = lr.predict_proba(xs.reshape(-1,1))[:,1]
    plt.plot(xs, ys)
    plt.title("Logistic Regression Of Median Income Versus Market Present")
```

<br>
Due to the dataset not having a lot of values, and the lack of variance as seen from the tax bracket plots, there is a very slight, mostly negligble negative prediction line produced by the regression. When printing the accuracy, it is very low:<br>

```python
    y_pred = lr.predict_proba(X_test)
    print('Accuracy of logistic regression: {:.2f}'.format(lr.score(X_test, y_test)))
    
    # Prints: Accuracy of logistic regression: 0.58
```

<br>
With this model, there is not much to conclude besides the fact that there is weak correlation, although this could be due to the small amount of data and the way it is distributed thanks to the economic make up of New York City. In order to see other data views, I also decided to divide the data between being in the middle tax bracket (which contains the most farmer's market), and being out of it. Originally, I was going to divide the data by economic class, but because middle class is defined as being in between $10,000 and $90,000 (2019), a vast majority of markets would fall into "middle class" placements, rendering any data analysis pointless. Dividing by tax brackets was the next logical step, since there is enough of a split between the middle tax bracket and outside tax brackets.
<br>

