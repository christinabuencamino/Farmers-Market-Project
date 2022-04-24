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

<p align="center">
<img width="700px" src="https://github.com/christinabuencamino/Farmers-Market-Project/blob/5a0bb2f9641f48703e42edde42d42d9ae73a09df/Farmers-Market-Locations.png" />
</p><br>

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
    
    # Optionally save and open in browser
    m.save("Farmers-Markets-Map.html")
    webbrowser.open('Farmers-Markets-Map.html')
```

