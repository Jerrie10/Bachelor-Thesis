import numpy as np
import geopy.distance as gpd
import pandas as pd
import requests
import json


""" Program that uses the initial schedule to estimate OD demands. All busses are assumed to be half-
full all the time, where OD demands are stated as if every passenger gets off at the stop after they 
get on the bus.

If busschedule (supply of transportation) would be equal to the demand for transportation, this 
occupancy rate would be accurate. It probably is not, as some lines are required a minimum frequency 
by the government and boarding rates of busses are probably not as equally distributed over bus stops, 
being more concentrated around trainstations instead.
"""

od_output = "./Data/od_data.txt"
routes_input = "./RawData/routes.csv"
stops_input = "./Intermediate/stopID_times.csv"

assumed_occupancy = 25  # Half full bus with capacity 50
hours_in_day = 9        # Opening hours of GP

# Get frequencies per route
frequencies = {}    # RouteID : frequency
routes_frame = pd.read_csv(routes_input, sep=";")
for i, row in routes_frame.iterrows():
    frequencies[int(row["ID"])] = int(row["frequency"])

# Get volume per busstop pair (u,v)
volumes = {}        # (u,v) : daily volume
stops_frame = pd.read_csv(stops_input)
#print(stops_frame)
for r in range(1, 1 + len(frequencies)):
    u = -1
    for i, row in stops_frame.iterrows():
        if (int(row["route_ID"]) == r):
            v = int(row["StopID"])
            #print(f"({u}, {v})")
            if u == -1:
                u = v
                #print(f"u verandert naar {v}")
                continue
            if (u, v) not in volumes:
                volumes[(u,v)] = 0
                #print(f"Adding ({u}, {v})")
            volumes[(u,v)] += hours_in_day * assumed_occupancy * frequencies[r]
            u = v

# Write volumes to file
with open(od_output, 'w') as fout:
    print("ID\tOrigin\tDestination\tVolume", file=fout)
    id = 0
    for arc in volumes:
        print(str(id)+"\t"+
              str(arc[0])+"\t"+
              str(arc[1])+"\t"+
              str(volumes[arc]),
              file=fout)
        id += 1

