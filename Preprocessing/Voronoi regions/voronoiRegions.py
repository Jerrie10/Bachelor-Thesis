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
def forceAspect(ax,aspect=1):
    im = ax.get_images()
    extent =  im[0].get_extent()
    ax.set_aspect(abs((extent[1]-extent[0])/(extent[3]-extent[2]))/aspect)


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
    
    regions = pd.read_csv(region_file, sep=';', skipinitialspace=True)
    vertices = pd.read_csv(vertices_file, skipinitialspace=True, index_col='ID')
    
    #coords = get_coords_csv(vertices_file, sep=';', skipinitialspace=True)
    fig, ax = plt.subplots()
    img = plt.imread("./Images/pc4_cropped.png")
    ax.imshow(img, extent=(4.435435, 4.550754, 52.116441, 52.18667))
    X, Y, ID = vertices['lat'], vertices['lng'], vertices.index

    # Drawing point numbers
    ax.scatter(X, Y, c='skyblue')
    for i in ID:
        ax.text(vertices.at[i, 'lat'], vertices.at[i, 'lng'], i, color='black', fontsize=8) # type: ignore
    
    # Drawing used edges
    for i, region in regions.iterrows():
        points = ast.literal_eval(region['Vertices'])
        if points == []: 
            # Empty list representing a point at infinity
            continue
        X, Y = [[],[]]
        for v in points:
            if v == -1:
                print(f"Found -1 in region {region}")
                ax.plot(X, Y, c='darkgrey', alpha=1)
                X, Y = [[],[]]
                continue
            X.append(vertices.at[v, 'lat'])
            Y.append(vertices.at[v, 'lng']) 
        X.append(vertices.at[points[0], 'lat'])
        Y.append(vertices.at[points[0], 'lng'])
        ax.plot(X, Y, c='darkgrey', alpha=1)
    
    # Drawing Voronoi weight points
    vor_weightpoints = pd.read_csv("./Voronoi regions/vorPoints.csv", skipinitialspace=True)
    vor_surface = pd.read_csv("./Voronoi regions/vorsurface.csv", sep=';', skipinitialspace=True)
    Xbus, Ybus, IDbus = vor_weightpoints['lat'], vor_weightpoints['lng'], vor_weightpoints['ID']    
    ax.scatter(Xbus, Ybus, color='maroon')
    for i in range(len(Ybus)):
        id = vor_weightpoints.at[i, 'region']
        #if vor_surface.at[id, 'Accounted'] == 1:
        #    continue
        ax.text(Xbus[i], Ybus[i], id, color='black', fontsize=8) # type: ignore
    
    
    plt.ylim(52.1195913, 52.18385562)
    plt.xlim(4.439670482, 4.52402989)
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

    regions = pd.read_csv(region_file, sep=";", skipinitialspace=True)
    vertices = pd.read_csv(vertices_file, skipinitialspace=True, index_col='ID')

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
        ax.text(Xbus[i], Ybus[i], busstops.at[i, 'region'], color='black', fontsize=8) # type: ignore
    
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


def overlay_border_voronoi():
    vor_region = pd.read_csv("./Voronoi regions/vorRegionsTemp.csv", sep=';', skipinitialspace=True)
    #vor_vertex = pd.read_csv("./Voronoi regions/voronoiVertices.csv", skipinitialspace=True)
    vor_weightpoints = pd.read_csv("./Voronoi regions/vorPoints.csv", skipinitialspace=True)
    #border_points = pd.read_csv("./Voronoi regions/extraVertices.csv", skipinitialspace=True)
    pc4_region = pd.read_csv("./Voronoi regions/pc4Regions.csv", sep=';', skipinitialspace=True)
    #pc4_vertex = pd.read_csv("./Voronoi regions/pc4Verticeslatlng.csv", sep=';')
    vertices = pd.read_csv("./Voronoi regions/vertices.csv",
                            skipinitialspace=True, 
                            index_col='ID')

    # Plot voronoi, with ID on weightpoints and vertices -------------------------------------------
    fig, ax = plt.subplots()
    ## Voronoi vertices and weightpoints
    Xbus, Ybus, IDbus = vor_weightpoints['lat'], vor_weightpoints['lng'], vor_weightpoints['ID']
    Xver, Yver, IDver = vertices['lat'], vertices['lng'], vertices.index
    ax.scatter(Xver, Yver, color='lightblue')
    for i in IDver:
        ax.text(vertices.at[i, 'lat'], vertices.at[i, 'lng'], i, color='black', fontsize=8) # type: ignore
    ax.scatter(Xbus, Ybus, color='blue')
    for i in range(len(Ybus)):
        ax.text(Xbus[i], Ybus[i], vor_weightpoints.at[i, 'region'], color='black', fontsize=8) # type: ignore
    
    ## Voronoi edges
    for i, region in vor_region.iterrows():
        points = ast.literal_eval(region['Vertices'])
        if points == []: 
            # Empty list representing a point at infinity
            continue
        X, Y = [[],[]]
        for v in points:
            if v == -1:
                print(f"Found -1 in region {region}")
                ax.plot(X, Y, c='darkgrey', alpha=1)
                X, Y = [[],[]]
                continue
            X.append(vertices.at[v, 'lat'])
            Y.append(vertices.at[v, 'lng']) 
        X.append(vertices.at[points[0], 'lat'])
        Y.append(vertices.at[points[0], 'lng'])
        ax.plot(X, Y, c='darkgrey', alpha=1)
    """
    # Plot borderpoints over voronoi, with ID on vertices ------------------------------------------
    Xborder, Yborder = border_points['lat'], border_points['lng']
    ax.scatter(Xborder, Yborder, color='orange')
    for i in range(len(Yborder)):
        ax.text(Xborder[i], Yborder[i], str(i + 301), color='black', fontsize=8)
    
    # Plot pc4 over voronoi, with ID on vertices ---------------------------------------------------
    Xpc4, Ypc4 = pc4_vertex['lat'], pc4_vertex['lng']
    ax.scatter(Xpc4, Ypc4, color='red')
    for i in range(len(Ypc4)):
        ax.text(Xpc4[i], Ypc4[i], str(i + 200), color='black', fontsize=8)
    
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
        ax.plot(X, Y, c='dimgrey', alpha=1)
    """

    plt.ylim(52.1195913, 52.18385562)
    plt.xlim(4.439670482, 4.52402989)
    plt.show()


def pc4_dots():
    ''' Function that draws community centers on picture of pc4 regions'''

    fig, ax = plt.subplots()
    img = plt.imread('./Images/pc4_cropped.png')
    ax.imshow(img, extent=(4.435435, 4.550754, 52.116441, 52.18667))

    points = pd.read_csv('./RawData/pc4.csv', sep=';')
    
    X, Y = [[],[]]
    for i, row in points.iterrows():
        x, y = float(row['lng'].replace(',', '.')), float(row['lat'].replace(',', '.'))
        
        X.append(x)
        Y.append(y)
        ax.text(x, y, row['ID'])

    ax.scatter(X, Y)
    ax.set_axis_off()
    plt.ylim(52.1195913, 52.18385562)
    plt.xlim(4.439670482, 4.52402989)
    plt.show()
    pass

def vor_regions_on_pc4():
    ''' Function that draws community centers points and voronoi regions on picture of pc4
    '''

    fig, ax = plt.subplots()
    img = plt.imread('./Images/pc4_cropped.png')
    ax.imshow(img, extent=(4.435435, 4.550754, 52.116441, 52.18667))

    # Draw community centers
    points = pd.read_csv('./Voronoi regions/Voronoi populations.csv', sep=';') # TODO Find good points file
    X, Y = [[],[]]
    for i, row in points.iterrows():
        x, y = float(row['lng'].replace(',', '.')), float(row['lat'].replace(',', '.'))
        X.append(x)
        Y.append(y)
        ax.text(x, y, row['ID'], size='xx-small')
    ax.scatter(X, Y)
    
    # Draw region edges
    regions = pd.read_csv('./Voronoi regions/vorRegionsTemp.csv', sep=';', skipinitialspace=True)
    vertices = pd.read_csv('./Voronoi regions/vertices.csv', skipinitialspace=True, index_col='ID')
    for i, region in regions.iterrows():
        points = ast.literal_eval(region['Vertices'])
        if points == []: 
            # Empty list representing a point at infinity
            continue
        X, Y = [[],[]]
        for v in points:
            if v == -1:
                print(f"Found -1 in region {region}")
                ax.plot(X, Y, c='darkgrey', alpha=1)
                X, Y = [[],[]]
                continue
            X.append(vertices.at[v, 'lat'])
            Y.append(vertices.at[v, 'lng']) 
        X.append(vertices.at[points[0], 'lat'])
        Y.append(vertices.at[points[0], 'lng'])
        ax.plot(X, Y, c='darkgrey', alpha=1)

    

    ax.set_axis_off()
    plt.ylim(52.1195913, 52.18385562)
    plt.xlim(4.439670482, 4.52402989)
    plt.show()
    pass

# Main =============================================================================================
def main():
    #draw_voronoi()
    #get_pc4_vertices()
    #transform_pixelcoord_to_latlng()
    #plot_points()
    '''
    calculate_surface("./Voronoi regions/pc4Regions.csv", 
                      "./Voronoi regions/pc4Verticeslatlng.csv", 
                      "./Voronoi regions/pc4surface.csv")
    '''
    #draw_regions("./Voronoi regions/vorRegionsTemp.csv","./Voronoi regions/vertices.csv")
    #overlay_pc4_voronoi()
    #overlay_border_voronoi()
    #pc4_dots()
    vor_regions_on_pc4()
    pass

main()