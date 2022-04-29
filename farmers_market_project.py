"""
Name:       Christina Buencamino
Email:      christina.buencamino28@myhunter.cuny.edu
Resources:  Repo link: https://github.com/christinabuencamino/Farmers-Market-Project
            Market data: https://data.cityofnewyork.us/dataset/DOHMH-Farmers-Markets/8vwk-6iz2/data
            GeoJSON data: https://data.beta.nyc/dataset/nyc-zip-code-tabulation-areas/resource/6df127b1-6d04-4bb7-b983-07402a2c3f90
                          https://github.com/fedhere/PUI2015_EC/blob/master/mam1612_EC/nyc-zip-code-tabulation-areas-polygons.geojson
            GeoJSON help: https://stjohn.github.io/teaching/seminar4/s17/cw6.html
            Folium help: https://medium.com/@meganlyons_79212/creating-maps-with-folium-baa6ff0f5c44
                         https://levelup.gitconnected.com/visualizing-housing-data-with-folium-maps-4718ed3452c2
                         https://medium.com/@saidakbarp/interactive-map-visualization-with-folium-in-python-2e95544d8d9b
                         https://towardsdatascience.com/visualizing-data-at-the-zip-code-level-with-folium-d07ac983db20
                         https://medium.com/datadream/mapping-with-folium-a-tale-of-3-cities-8e5ab7f4e53d
                         https://github.com/python-visualization/folium/issues/1404
            Geopy help: https://www.geeksforgeeks.org/get-zip-code-with-given-location-using-geopy-in-python/
            Credit for zip code help: https://gis.stackexchange.com/questions/352961/convert-lat-lon-to-zip-postal-code-using-python
            Regex help: https://stackoverflow.com/questions/53962844/applying-regex-across-entire-column-of-a-dataframe
            Pandas: https://groups.google.com/g/pyqtgraph/c/trmr_5dV6Uc?pli=1
            Logistic Reg: http://www.textbook.ds100.org/ch/24/classification_log_reg.html
Title:      Does The Presence Of A Farmer's Market In A Zip Code Predict Resident Median Income?
URL:        https://christinabuencamino.github.io/Farmers-Market-Project/
"""

import geopy
import webbrowser
import pandas as pd
import regex as re
import folium
from folium.plugins import BeautifyIcon
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn import preprocessing
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
import numpy as np
from sklearn.feature_extraction import DictVectorizer


# Data creation/modification  ******************************************************************************************

'''
Helper function to call geolocator for calculating farmer's market zip codes.
https://gis.stackexchange.com/questions/352961/convert-lat-lon-to-zip-postal-code-using-python
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

    # I had to split this into three calls because one call would time out geopy
    # For testing, I saved this csv and called my local file
    markets_1 = markets.iloc[:50,:]
    zipcodes_1 = markets_1.apply(get_zipcode, axis=1, geolocator=locator, lat='Latitude', lon='Longitude')
    zipcodes_1 = zipcodes_1.replace('112321', '11232')

    markets_2 = markets.iloc[50:100,:]
    zipcodes_2 = markets_2.apply(get_zipcode, axis=1, geolocator=locator, lat='Latitude', lon='Longitude')

    markets_3 = markets.iloc[100:,:]
    zipcodes_3 = markets_3.apply(get_zipcode, axis=1, geolocator=locator, lat='Latitude', lon='Longitude')

    zipcodes = zipcodes_1.append(zipcodes_2)
    zipcodes = zipcodes.append(zipcodes_3)

    zipcodes.name = 'Market_Present'

    return zipcodes


'''
Calls zip code and median_data functions and merges them together to create complete dataframe for analysis.
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
Cleans up Median income csv to only include zip code and 2019 median income per zipcode, while fixing data types.
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


# Functions for generating maps ****************************************************************************************

'''
Creates a folium map with NYC geojson data borders and farmer's market locations starred.
'''
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

    # m.save()
    # webbrowser.open()


'''
Creates a choropleth map of median income per zipcode in NYC using geojson data and median income data.
'''
def CreateMedianChoropleth():
    median_data = CreateMedianData()

    # Create map using geojson data boundaries to connect with zip codes from csv, and coloring based on income
    m = folium.Map(location=[40.75, -74], zoom_start=11.4)
    folium.TileLayer('cartodbpositron').add_to(m)
    m.choropleth(geo_data='ZipCodeGeo.json', fill_color='YlGnBu', fill_opacity=0.9, line_opacity=0.5,
                 data=median_data,
                 threshold_scale = [0, 10276, 41775, 89075, 170050, 215950, 250001],
                 key_on='feature.properties.postalCode',
                 columns=['NAME', 'S1903_C03_001E'],
                 nan_fill_color='white',
                 legend_name='Median Income')

    # m.save()
    # webbrowser.open()


'''
Creates the merged version of the farmer's market map and median income choropleth map.
'''
def CreateMedianMarketMap():
    median_data = CreateMedianData()

    # Create map, now with choropleth shading and also market markers
    m = folium.Map(location=[40.75, -74], zoom_start=11.4)
    folium.TileLayer('cartodbpositron').add_to(m)
    m.choropleth(geo_data='ZipCodeGeo.json',
                 fill_color='YlGnBu', fill_opacity=0.9, line_opacity=0.5,
                 data=median_data,
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


# Functions for generating bar graphs **********************************************************************************

'''
Creates a bar plot of the number of farmer's markets per borough.
'''
def GenerateBoroughBarPlot(market_csv):
    # Cleanup farmer's market csv
    market = pd.read_csv(market_csv)
    market = market['Borough'].value_counts().reset_index(
        inplace=False)  # Create dataframe of each borough and their count of markets
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


'''
Creates a bar plot of the number of farmer's markets located in a certain tax bracket in NYC.
'''
def GenerateTaxPlot():
    # Get graph data and isolate zip codes with markets
    combined_df = CombineMedianMarket()
    combined_df = combined_df[combined_df['Market_Present'] == 1]

    # Categorize data into tax brackets
    taxes = [0, 10276, 41775, 89075, 170050, 215950, 250001]
    labels = ['$0 - $10276', '$10276 - $41775', '$41775 - $89075', '$89075 - $170050', '$170050 - $215950', '215950+']
    combined_df['Tax_Bracket'] = pd.cut(combined_df['S1903_C03_001E'], taxes, labels=labels, ordered=False)

    # Fix indexing
    brackets = combined_df['Tax_Bracket'].value_counts().to_frame()
    brackets = brackets.reindex(labels)

    # Create bar plot
    fig, ax = plt.subplots()
    sns.barplot(x=brackets.index, y=brackets['Tax_Bracket'], data=brackets,
                             color="salmon")
    plt.xticks(rotation=30)
    ax.set_xlabel('Tax Brackets')
    ax.set_ylabel('Number of Farmers Markets')
    ax.set_title("Number Of Markets Per Zip Code's Tax Bracket In NYC")


'''
Creates a double bar histogram of markets and zipcode in a bracket.
'''
def GenerateDoubleBar():
    combined_df = CombineMedianMarket()

    # Create tax bracket column
    taxes = [0, 10276, 41775, 89075, 170050, 215950, 250001]
    labels = ['$0 - $10276', '$10276 - $41775', '$41775 - $89075', '$89075 - $170050', '$170050 - $215950', '215950+']
    combined_df['Tax_Bracket'] = pd.cut(combined_df['S1903_C03_001E'], taxes, labels=labels, ordered=False)

    # Get count of each tax bracket no matter if there is a farmer's market
    tax_df = combined_df.groupby(['Tax_Bracket']).count()
    tax_df.reset_index(inplace=True)
    tax_df = tax_df[['Tax_Bracket', 'NAME']]

    # Get count of each tax bracket, with only zip codes that have a farmer's market
    markets = combined_df[combined_df['Market_Present'] == 1].groupby(['Tax_Bracket']).count()
    markets.reset_index(inplace=True)
    markets = markets[['Tax_Bracket', 'Market_Present']]

    # Merge data to have with/without market data in same df
    merged = pd.merge(tax_df, markets, on='Tax_Bracket')

    # Create bar graph
    ax = merged.plot(x='Tax_Bracket', y=['NAME', 'Market_Present'], kind='bar', color=['salmon', 'lightgreen'])
    ax.set_xlabel('Tax Bracket')
    ax.set_ylabel('Number Of Occurrences')
    ax.set_title("Number Of Zip Codes And Farmer's Markets Per Tax Bracket In NYC")
    plt.xticks(rotation=30)
    ax.legend(["Zip Codes", "Farmer's Markets"])

    plt.show()


'''
** Unused function. 
Created a boolean column of whether or not a zip code was in the center tax bracket.
Could not find a way to conduct a meaningful analysis with this column.
'''
def CreateMiddleBar():
    # Get graph data and isolate zip codes with markets
    combined_df = CombineMedianMarket()
    combined_df = combined_df[combined_df['Market_Present'] == 1]

    # Categorize data into tax brackets
    taxes = [0, 10276, 41775, 89075, 170050, 215950, 250001]
    labels = ['$0 - $10276', '$10276 - $41775', '$41775 - $89075', '$89075 - $170050', '$170050 - $215950', '215950+']
    combined_df['Tax_Bracket'] = pd.cut(combined_df['S1903_C03_001E'], taxes, labels=labels, ordered=False)

    combined_df['Middle_Tax'] = 'Yes'
    combined_df.loc[combined_df['Tax_Bracket'] != '$41775 - $89075', 'Middle_Tax'] = 'No'

    b = combined_df['Middle_Tax'].value_counts().to_frame()
    b.reset_index(inplace=True)
    b = b.rename(columns={'index':'Within Middle Income', 'Middle_Tax':'Number Of Zip Codes'})

    x = b.plot.bar(x='Within Middle Income', y='Number Of Zip Codes', rot=0, color='salmon')

    plt.show()


# Functions for models + predictions ***********************************************************************************
'''
Run a logistic regression of if a market is present and the median income of a zip code, plot regression,
and create and plot confusion matrix.
'''
def LogRegAndConfMatrix():
    combined_df = CombineMedianMarket()

    # Run logistic regression on income and boolean market_present column
    X = combined_df[['S1903_C03_001E']]
    y = combined_df['Market_Present'].to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42)
    lr = LogisticRegression()
    lr.fit(X_train, y_train)
    # print(lr.score(X_test, y_test))

    y_pred = lr.predict(X_test)

    # Plot linear regression
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
    # plt.show()

    # print('Accuracy of logistic regression: {:.2f}'.format(lr.score(X_test, y_test)))

    # Create and plot confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    ax = sns.heatmap(cm, annot=True, cmap='Reds')

    ax.set_title('Confusion Matrix\n\n')
    ax.set_xlabel('\nPredicted Values')
    ax.set_ylabel('Actual Values ')

    ax.xaxis.set_ticklabels(['False', 'True'])
    ax.yaxis.set_ticklabels(['False', 'True'])

    plt.show()

