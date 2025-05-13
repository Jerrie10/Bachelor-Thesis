import numpy as np
import pandas as pd
import geopy.distance as gpd
from scipy.spatial import Voronoi, voronoi_plot_2d
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.transforms import Affine2D
import os
#from PIL import Image

""" Program that can make illustrations of the multiple graphs 
and maps
"""

# -------------------------------------------------------------------------------------------------
def get_coords(file: str) -> list:
    """ Converts csv file to list of coordinates, needs csv file
    with ; separator and columns named 'lat', 'lng'
    """
    filename, file_extension = os.path.splitext(file)
    if (file_extension) != ".csv":
        print(f"{file} is not a csv file!")
        return -1
    
    coords = []
    df = pd.read_csv(file, sep=';')
    for i, row in df.iterrows():
        coords.append([float(row['lng'].replace(",", ".")), 
                       float(row['lat'].replace(",", "."))])
    
    return coords

# -------------------------------------------------------------------------------------------------
def forceAspect(ax,aspect=1):
    im = ax.get_images()
    extent =  im[0].get_extent()
    ax.set_aspect(abs((extent[1]-extent[0])/(extent[3]-extent[2]))/aspect)

# -------------------------------------------------------------------------------------------------
def draw_voronoi():
    """ Draws a voronoi diagram on a map of Leiden. Busstops are used as 'weightpoints' in diagram.
    Alignment is close enough, could be better.
    """
    busstop_coords = get_coords("RawData/busstops.csv")
    
    img = plt.imread('Images/pc4_cropped.png')
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[4.435435, 4.55486, 52.116441, 52.18667])
    forceAspect(ax)

    points = np.array(busstop_coords)
    vor = Voronoi(points)
    voronoi_plot_2d(vor, point_size=10, ax=ax, show_vertices =False)
    
    plt.show()

def draw_buslines():
    pass

def main():
    

    pass

main()