import numpy as np
import geopy.distance as gpd

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


