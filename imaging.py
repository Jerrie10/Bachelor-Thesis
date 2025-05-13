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
def get_transform_2pts(q1, q2, p1, p2):
    """ create transform to transform from q to p, 
        such that q1 will point to p1, and q2 to p2 
    """
    ang = np.arctan((p2-p1)[1] /(p2-p1)[0])-np.arctan((q2-q1)[1] /(q2-q1)[0])
    s = np.abs(np.sqrt(np.sum((p2-p1)**2))/np.sqrt(np.sum((q2-q1)**2)))
    trans = Affine2D().translate(*-q1).rotate(ang).scale(s).translate(*p1)
    return trans

# -------------------------------------------------------------------------------------------------
def useless_function(coords: list): # Does not work properly, do not use
    image = plt.imread('Images/pc4.png')
    print(image.shape)
    y0 = image.shape[0]
    points = np.array(coords)
    vor = Voronoi(points)
    waypoints = [[0, 1, 4, 6, 6], [0, 0, 4, 4, 3]]

    # Coordinates for transformation.
    lc1 = np.array([0,0])
    #lc1 = np.array([52.118540, 4.437844])
    ic1 = np.array([828,861])#[4, y0-788]
    lc2 = np.array([1,0])
    #lc2 = np.array([52.186173, 4.521118])
    ic2 = np.array([728,861])#[615, y0-26]
    trans = get_transform_2pts(lc1, lc2, ic1, ic2)

    fig, ax = plt.subplots()
    ax.imshow(np.flipud(image), origin="lower")
    
    #voronoi_plot_2d(vor, point_size=10, show_vertices =False)

    plt.plot(waypoints[0], waypoints[1], 'o-') #, transform=trans+ax.transData

    ax.set_aspect("equal")
    plt.show()
    plt.savefig('Images/picture.png')


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

def main():
    draw_voronoi()

main()