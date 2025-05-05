import numpy as np
import geopy.distance as gpd
import pandas as pd
import requests
import json


def address_to_coords(inputfile, outputfile):
    """Uses the MapQuestAPI to get coordinates of locations, based on adress
    """
    private = json.load(open("private.json", 'r'))
    api_key = private['MapQuest']
    
    
    df = pd.read_csv(inputfile, sep=';')
    pd.set_option('display.max_rows', None)

    for i, row in df.iterrows():
        apiAddress = str(df.at[i,'Adres'])
        
        parameters = {
            "key": api_key,
            "location": apiAddress
        }

        response = requests.get("http://www.mapquestapi.com/geocoding/v1/address", params=parameters)
        
        data = response.text
        dataJ = json.loads(data)['results']
        lat = (dataJ[0]['locations'][0]['latLng']['lat'])
        lng = (dataJ[0]['locations'][0]['latLng']['lng'])
        
        df.at[i,'lat'] = lat
        df.at[i,'lng'] = lng
        
    df.to_csv(outputfile)

def distance(x, y, taxicab=False):
    """Calculates geodesic distance (km) between two tuples of coordinates.

    Accepts an optional argument indicating whether to use taxicab distance
    instead of the default Euclidean distance.
    """

    if taxicab == False:
        return gpd.geodesic(x, y).km
    else:
        return min(gpd.geodesic(x, (x[0],y[1])).km +
                   gpd.geodesic((x[0],y[1]), y).km, gpd.geodesic(x,
                               (y[0],x[1])).km + gpd.geodesic((y[0],x[1]),
                               y).km)


def main():
    address_to_coords("RawData/healthlocations.csv", "Data/healthdata.csv")


main()