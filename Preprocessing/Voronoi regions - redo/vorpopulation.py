import numpy as np
import pandas as pd
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import os
import networkx as nx
import ast
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

""" Program that imports weightpoints (busstops) and creates Voronoi regions. It also imports known
population regions (PC4) and distributes population over voronoi regions.

Imaging functionality is also added"""


## Files        ====================================================================================
weightpoints_file = './Preprocessing/RawData/busstops.csv'
known_population_file = './Preprocessing/RawData/pc4.csv'
known_region_file = './Preprocessing/Voronoi regions/pc4Regions.csv'
known_vertices_file = './Preprocessing/Voronoi regions/pc4Verticeslatlng.csv'

vor_pop_output = './Preprocessing/RawData/vorpop.csv'


def draw_regions(region_file, vertices_file):
    """Function that visualizes the regions made with plot_points. Does everything plot_points does
    and more."""
    
    regions = pd.read_csv(region_file, sep=';', skipinitialspace=True)
    vertices = pd.read_csv(vertices_file, sep=';', skipinitialspace=True, index_col='ID')
    
    
    #coords = get_coords_csv(vertices_file, sep=';', skipinitialspace=True)
    fig, ax = plt.subplots()
    img = plt.imread('./Imaging/Images/pc4_cropped.png')
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
                print(f'Found -1 in region {region}')
                ax.plot(X, Y, c='darkgrey', alpha=1)
                X, Y = [[],[]]
                continue
            X.append(vertices.at[v, 'lat'])
            Y.append(vertices.at[v, 'lng']) 
        X.append(vertices.at[points[0], 'lat'])
        Y.append(vertices.at[points[0], 'lng'])
        ax.plot(X, Y, c='darkgrey', alpha=1)
    
    """
    # Drawing Voronoi weight points
    vor_weightpoints = pd.read_csv('./Voronoi regions/vorPoints.csv', skipinitialspace=True)
    vor_surface = pd.read_csv('./Voronoi regions/vorsurface.csv', sep=';', skipinitialspace=True)
    Xbus, Ybus, IDbus = vor_weightpoints['lat'], vor_weightpoints['lng'], vor_weightpoints['ID']    
    ax.scatter(Xbus, Ybus, color='maroon')
    for i in range(len(Ybus)):
        id = vor_weightpoints.at[i, 'region']
        #if vor_surface.at[id, 'Accounted'] == 1:
        #    continue
        ax.text(Xbus[i], Ybus[i], id, color='black', fontsize=8) # type: ignore
    """
    
    plt.ylim(52.1195913, 52.18385562)
    plt.xlim(4.439670482, 4.52402989)
    plt.show()


def rewrite_pc4_regions():
    """Used one time to add 200 to all vertex numbers in pc4Regions.csv"""
    regions = pd.read_csv(known_region_file, sep=';', skipinitialspace=True, index_col='ID')
    print(regions)

    for i, region in regions.iterrows():
        oldlist = ast.literal_eval(region['Vertices'])
        newlist = []
        for number in oldlist:
            newlist.append(number+200)
        region['Vertices'] = str(newlist)
    print(regions)
    regions.to_csv('./Preprocessing/Voronoi regions/new_pc4Regions.csv', sep=';', index_label='ID')
    

def vertex_to_point(v: int, vertices = pd.DataFrame) -> Point:
    #p = Point(vertices.at[v, 'lng'], vertices.at[v, 'lat'])
    p = Point(1, 1)

    return p

def find_intersections(A, B, vertices) -> pd.DataFrame: 
    """Function that finds pairwise intersections of two sets of polygons.
    Returns dataframe C
    
    Parameters
    --------
    A : pandas.DataFrame instance
        ID; list[int] of vertex indices 
    B : same as A
    vertices : dictionary 
        linking vertex ID to coordinates
    C : pandas.Dataframe instance
        ID; list[int] ; parent a ; parent b
        
        
    """
    header = ['Vertices', 'a', 'b']
    C = pd.DataFrame(columns = header)
    

    return C

def main():
    #A, B = [[],[]]
    #find_intersections(A, B)
    
    weightpoints = pd.read_csv(weightpoints_file, sep=';', index_col='ID')
    coords = []
    for i, row in weightpoints.iterrows():
        if (len(coords) < 1000):
            coords.append([float(row['lng'].replace(",", ".")), float(row['lat'].replace(",", "."))])
    vor = Voronoi(np.array(coords))
    
    with open("./Preprocessing/Voronoi regions - redo/vorRegions.csv", 'w') as fout:
        print("ID ; Vertices", file=fout)
        id = 0
        for reg in vor.regions:
            print(f"{id}; {reg}", file=fout)
            id += 1
    
    with open("./Preprocessing/Voronoi regions - redo/voronoiVertices.csv", 'w') as fout:
        print("ID, lat, lng", file=fout)
        id = 0
        for coord in vor.vertices:
            print(f"{id}, {coord[0]}, {coord[1]}", file=fout)
            id += 1
    
    
    with open("./Preprocessing/Voronoi regions - redo/vorPoints.csv", 'w') as fout:
        print("ID, lat, lng, region", file=fout)
        id = 0
        for coord in vor.points:
            print(f"{id}, {coord[0]}, {coord[1]}, {vor.point_region[id]}", file=fout)
            id += 1
    
    voronoi_plot_2d(vor)
    
    plt.ylim(52.1195913, 52.18385562)
    plt.xlim(4.439670482, 4.52402989)
    plt.show()
    
    
    pass
main()