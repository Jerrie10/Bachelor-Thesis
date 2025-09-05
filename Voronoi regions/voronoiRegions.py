import numpy as np
import pandas as pd
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import os
import networkx as nx
import ast

""" Program that can export the found voronoi regions, calculates their surface area and assigns 
population based on surface area
"""

# -------------------------------------------------------------------------------------------------
def get_coords(file: str) -> list:
    """ Converts csv file to list of coordinates, needs csv file
    with ; separator and columns named 'lat', 'lng'
    """

    coords = []

    filename, file_extension = os.path.splitext(file)
    if (file_extension) != ".csv":
        print(f"{file} is not a csv file!")
        return coords
    
    df = pd.read_csv(file, sep=';')
    for i, row in df.iterrows():
        coords.append([float(row['lng'].replace(",", ".")), 
                       float(row['lat'].replace(",", "."))])
    
    return coords

def get_coords_csv(file: str) -> list:
    """ Converts csv file to list of coordinates, needs csv file
    with , separator and columns named 'lat', 'lng'
    """

    coords = []

    filename, file_extension = os.path.splitext(file)
    if (file_extension) != ".csv":
        print(f"{file} is not a csv file!")
        return coords
    
    df = pd.read_csv(file)
    for i, row in df.iterrows():
        coords.append([float(row['lng']), 
                       float(row['lat'])])
    
    return coords

# -------------------------------------------------------------------------------------------------
def draw_voronoi():
    """ Draws a voronoi diagram on a map of Leiden. Busstops are used as 'weightpoints' in diagram.
    Alignment is close enough, could be better.
    """
    busstop_coords = get_coords("./RawData/busstops.csv")
    
    """img = plt.imread('Images/pc4_cropped.png')
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[4.435435, 4.550754, 52.116441, 52.18667])
    forceAspect(ax)
    plt.xticks([]) 
    plt.yticks([])
     """
    points = np.array(busstop_coords)
    vor = Voronoi(points)
    
    
    """
    with open("./Voronoi regions/vorRegions.csv", 'w') as fout:
        print("ID ; Vertices", file=fout)
        id = 0
        for reg in vor.regions:
            print(f"{id}; {reg}", file=fout)
            id += 1
    
    with open("./Voronoi regions/voronoiVertices.csv", 'w') as fout:
        print("ID, lat, lng", file=fout)
        id = 0
        for coord in vor.vertices:
            print(f"{id}, {coord[0]}, {coord[1]}", file=fout)
            id += 1
    
    
    with open("./Voronoi regions/vorPoints.csv", 'w') as fout:
        print("ID, lat, lng, region", file=fout)
        id = 0
        for coord in vor.points:
            print(f"{id}, {coord[0]}, {coord[1]}, {vor.point_region[id]}", file=fout)
            id += 1
     """   
    voronoi_plot_2d(vor, point_size=10, show_points=False, show_vertices =True)
    plt.show()


# PC4 Gebieden tekenen =============================================================================
def get_pc4_vertices():
    # Lijst van gebieden, elk gebied is een lijst met punten
    points = []

    fig, ax = plt.subplots()
    img = plt.imread("./Images/pc4_voronoi_overlay.png") #./Images/pc4_cropped.png
    ax.imshow(img)

    # Klik-event
    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            x, y = event.xdata, event.ydata
            points.append((x, y))
            idx = len(points) + 300  # point index (starting at 300)
            
            # Punt tekenen
            ax.scatter(x, y, c='red')
            # Nummer erbij schrijven
            ax.text(x, y, str(idx), color='yellow', fontsize=12, weight='bold')
            
            plt.draw()
            print(f"Punt {idx}: ({x:.2f}, {y:.2f})")


    # Event koppelen
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()

    # Printen
    print("Alle punten:")
    for i, (x, y) in enumerate(points, start=1):
        print(f"{i}: ({x:.2f}, {y:.2f})")
    

def transform_pixelcoord_to_latlng():
    pixels = get_coords_csv("./Voronoi regions/pc4VerticesPixels.csv")
    coords = []

    for pixel in pixels:
        # (0,0) naar linksonder
        y, x = pixel
        y = 807 - y

        # Hoekpunten: [4.435435, 4.550754, 52.116441, 52.18667]
        links = 4.435435
        rechts = 4.550754
        onder = 52.116441
        boven = 52.18667
        
        lng = onder + (boven - onder)*y/807
        lat = links + (rechts - links)*x/810
        coords.append([lng, lat])
    
    with open("pc4Verticeslatlng.csv", "w") as f:
        id = 0
        f.write("ID,lng,lat\n")
        for coord in coords:
            f.write(f"{id},{coord[0]},{coord[1]}\n")
            id+=1
    

def plot_points():
    """Plots points to assign bordering vertices to regions. If a regionsfile is available,
    draw_regions does a better job."""
    coords = get_coords_csv("./Voronoi regions/pc4VerticesPixels.csv")
    fig, ax = plt.subplots()
    img = plt.imread("./Images/pc4_cropped.png")
    ax.imshow(img)
    Y, X = zip(*coords)
    
    ax.scatter(X, Y, c='red')
    for i in range(len(Y)):
        ax.text(X[i], Y[i], str(i), color='black', fontsize=12)
    plt.show()

def draw_regions(region_file, vertices_file):
    """Function that visualizes the regions made with plot_points. Does everything plot_points does
    and more."""
    coords = get_coords_csv(vertices_file)
    fig, ax = plt.subplots()
    img = plt.imread("./Images/pc4_cropped.png")
    ax.imshow(img)
    Y, X = zip(*coords)
    
    # Drawing point numbers
    ax.scatter(X, Y, c='red')
    for i in range(len(Y)):
        ax.text(X[i], Y[i], str(i), color='black', fontsize=8)
    
    # Drawing used edges
    regions = pd.read_csv(region_file, sep=";", skipinitialspace=True)
    vertices = pd.read_csv(vertices_file)
    
    
    for i, region in regions.iterrows():
        points = ast.literal_eval(region['Vertices'])
        X, Y = [[],[]]
        for v in points:
            X.append(vertices.at[v, 'lat'])
            Y.append(vertices.at[v, 'lng']) 
        X.append(vertices.at[points[0], 'lat'])
        Y.append(vertices.at[points[0], 'lng'])
        ax.plot(X, Y, c='blue')
    plt.show()
    
    
def calculate_surface(region_file, vertices_file, output_file):
    """ Function that calculates surface area of regions.
    region_file is formatted as 'ID; Vertices' csvfile where ID is an int and Vertices is a list of 
        ints. vertices are the boundary of the region in a clockwise order
    vertices_file is formatted as 'ID, lng, lat' where ID is an int and lng, lat are floats
        representing coordinate location.
    Function outputs in a csvfile formatted as 'ID, Vertices, area' where ID is the regionID, 
        Vertices is a list of ints and area is a float in square kilometers.
    """

    vertices = pd.read_csv(vertices_file)
    regions = pd.read_csv(region_file, sep=";", skipinitialspace=True)
    
    # Using edges of picture as ruler
    # Cornerpoints: [4.435435, 4.550754, 52.116441, 52.18667]
    # 810 pixels wide = 7,5 km = 0.115319 degrees -> 0.01537587 degrees per km
    # 807 pixels high  = 7  km = 0.070229 degrees -> 0.01003271 degrees per km
    
    # We take lowerleft corner as origin, assume earth is flat enough
    X, Y = [[],[]]
    lower = 52.116441
    vertical_step = 0.01003271
    left = 4.435435
    horizontal_step = 0.01537587
    for i, vertex in vertices.iterrows():
        X.append((vertex['lat'] - left) / horizontal_step)
        Y.append((vertex['lng'] - lower) / vertical_step)
    vertices.insert(len(vertices.columns), "X", X)
    vertices.insert(len(vertices.columns), "Y", Y)
    
    areas = []
    for i, region in regions.iterrows():
        points = ast.literal_eval(region['Vertices'])
        
        X, Y = [[],[]]
        for j in points:
            X.append(vertices.at[j, 'X'])
            Y.append(vertices.at[j, 'Y'])  
        area = 0.5*np.abs(np.dot(X,np.roll(Y,1))-np.dot(Y,np.roll(X,1)))
        areas.append(area)
    
    totaal = 0
    for a in areas:
        totaal += a
    print(f"Totale oppervlakte: {totaal}")
    regions.insert(len(regions.columns), "Surface area", areas)
    print(regions)
    regions.to_csv(output_file, sep=';', mode='x')

def overlay_pc4_voronoi():
    vor_region = pd.read_csv("./Voronoi regions/vorRegions.csv", sep=';', skipinitialspace=True)
    vor_vertex = pd.read_csv("./Voronoi regions/voronoiVertices.csv", skipinitialspace=True)
    pc4_region = pd.read_csv("./Voronoi regions/pc4Regions.csv", sep=';', skipinitialspace=True)
    pc4_vertex = pd.read_csv("./Voronoi regions/pc4Verticeslatlng.csv")
    busstops = pd.read_csv("./Voronoi regions/vorPoints.csv", skipinitialspace=True)
    
    
    # Plot voronoi, with ID on weightpoints and vertices
    fig, ax = plt.subplots()
    ## Voronoi vertices and weightpoints
    Xbus, Ybus = busstops['lat'], busstops['lng']
    Xvor, Yvor = vor_vertex['lat'], vor_vertex['lng']
    ax.scatter(Xvor, Yvor, color='lightblue')
    for i in range(len(Yvor)):
        ax.text(Xvor[i], Yvor[i], str(i), color='black', fontsize=8)
    ax.scatter(Xbus, Ybus, color='blue')
    for i in range(len(Ybus)):
        ax.text(Xbus[i], Ybus[i], busstops.at[i, 'region'], color='black', fontsize=8)
    
    ## Voronoi edges
    for i, region in vor_region.iterrows():
        points = ast.literal_eval(region['Vertices'])
        if points == []: 
            # Empty list representing a point at infinity
            continue
        X, Y = [[],[]]
        for v in points:
            if v == -1: 
                continue
            X.append(vor_vertex.at[v, 'lat'])
            Y.append(vor_vertex.at[v, 'lng']) 
        X.append(vor_vertex.at[points[0], 'lat'])
        Y.append(vor_vertex.at[points[0], 'lng'])
        ax.plot(X, Y, c='grey', alpha=0.25)
    
    # Plot pc4 over voronoi, with ID on vertices
    Xpc4, Ypc4 = pc4_vertex['lat'], pc4_vertex['lng']
    ax.scatter(Xpc4, Ypc4, color='red')
    for i in range(len(Ypc4)):
        ax.text(Xpc4[i], Ypc4[i], str(i), color='black', fontsize=8)
    
    ## pc4 edges
    for i, region in pc4_region.iterrows():
        points = ast.literal_eval(region['Vertices'])
        if points == []: 
            # Empty list representing a point at infinity
            continue
        X, Y = [[],[]]
        for v in points:
            if v == -1: 
                continue
            X.append(pc4_vertex.at[v, 'lat'])
            Y.append(pc4_vertex.at[v, 'lng']) 
        X.append(pc4_vertex.at[points[0], 'lat'])
        Y.append(pc4_vertex.at[points[0], 'lng'])
        ax.plot(X, Y, c='dimgrey', alpha=0.25)


    # Adding point so the voronoi regions are finite
    new_vertices = []
    ## Klik-event
    def onclick(event):
        if event.xdata is not None and event.ydata is not None:
            x, y = event.xdata, event.ydata
            new_vertices.append((x, y))
            idx = len(new_vertices) + 300  # point index (starting at 300)
            
            # Punt tekenen
            ax.scatter(x, y, c='orange')
            # Nummer erbij schrijven
            ax.text(x, y, str(idx), color='black', fontsize=12, weight='bold')
            
            plt.draw()
            print(f"Punt {idx}: ({x:.10f}, {y:.10f})")


    ## Event koppelen
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.ylim(52.1195913, 52.18385562)
    plt.xlim(4.439670482, 4.52402989)
    plt.show()


# Main =============================================================================================
def main():
    #draw_voronoi()
    #get_pc4_vertices()
    #transform_pixelcoord_to_latlng()
    #plot_points()
    #calculate_surface("./Voronoi regions/pc4Regions.csv", 
    #                  "./Voronoi regions/pc4Verticeslatlng.csv", 
    #                  "./Voronoi regions/pc4surface.csv")
    #draw_regions("./Voronoi regions/pc4Regions.csv", "./Voronoi regions/pc4VerticesPixels.csv")
    overlay_pc4_voronoi()
    pass

main()