import numpy as np
import pandas as pd
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import os
import networkx as nx
import ast
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely.plotting import plot_polygon

""" Program that imports weightpoints (busstops) and creates Voronoi regions. It also imports known
population regions (PC4) and distributes population over voronoi regions.

Imaging functionality is also added"""


## Files        ====================================================================================
weightpoints_file = './Preprocessing/RawData/busstops.csv'
known_population_file = './Preprocessing/RawData/pc4-georef.csv'
known_region_file = './Preprocessing/Voronoi regions/pc4Regions.csv'
known_vertices_file = './Preprocessing/Voronoi regions/pc4Verticeslatlng.csv'

vor_region_file = './Preprocessing/Voronoi regions - redo/vorRegions.csv'
vor_vertex_file = './Preprocessing/Voronoi regions - redo/voronoiVertices.csv'
vor_points_file = './Preprocessing/Voronoi regions - redo/vorPoints.csv'
pc4_shape_output = './Preprocessing/Voronoi regions - redo/pc4Shape.csv'

pc4_pop_output = './Preprocessing/RawData/pc4pop.csv'
vor_pop_output = './Preprocessing/RawData/vorpop.csv'

# Obsolete?
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

# Obsolete?
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
    
def vor_region():
    '''Makes voronoi diagram based on weightpoints, writes data to different files and shows plot'''
    weightpoints = pd.read_csv(weightpoints_file, sep=';', index_col='ID')
    coords = []
    for i, row in weightpoints.iterrows():
        if (len(coords) < 1000):
            coords.append([float(row['lng'].replace(',', '.')), 
                           float(row['lat'].replace(',', '.'))])
    vor = Voronoi(np.array(coords))
    
    with open('./Preprocessing/Voronoi regions - redo/vorRegions.csv', 'w') as fout:
        print('ID ; Vertices', file=fout)
        id = 0
        for reg in vor.regions:
            print(f'{id}; {reg}', file=fout)
            id += 1
    
    with open('./Preprocessing/Voronoi regions - redo/voronoiVertices.csv', 'w') as fout:
        print('ID, lat, lng', file=fout)
        id = 0
        for coord in vor.vertices:
            print(f'{id}, {coord[0]}, {coord[1]}', file=fout)
            id += 1
    
    
    with open('./Preprocessing/Voronoi regions - redo/vorPoints.csv', 'w') as fout:
        print('ID, lat, lng, region', file=fout)
        id = 0
        for coord in vor.points:
            print(f'{id}, {coord[0]}, {coord[1]}, {vor.point_region[id]}', file=fout)
            id += 1
    
    voronoi_plot_2d(vor)
    
    plt.ylim(52.1195913, 52.18385562)
    plt.xlim(4.439670482, 4.52402989)
    plt.show()

def pc4_region(infile, popfile, shapefile):
    ''' Processes pc4-georef.csv to pc4pop.csv'''
    in_frame = pd.read_csv(infile, sep=';')
    in_frame = in_frame.sort_values('PC4', ignore_index=True)

    # Population data per pc4 region
    pop_data = {2311: 11355, 2312: 15260, 2313: 12375, 2314: 6200,
                2315: 8715, 2316: 10725, 2317: 10720, 2318: 3245,
                2321: 12795, 2322: 225, 2323: 170, 2324: 9965,
                2331: 10705, 2332: 10545, 2333: 4300, 2334: 2805}

    pop_rows_list=[]
    shape_rows_list=[]
    for i, row in in_frame.iterrows():
        pop_dict = {}
        shape_dict = {}
        lat, lng = row['Geo Point'].split(', ')
        ID = row['PC4']
        pop = pop_data[ID]
        shape = str(row['Geo Shape'])
        n= shape.find('4')
        shape = shape[n-2:]
        m=shape.rfind(']')
        shape =shape[:m+1]
        pop_dict.update({
            'ID': ID,
            'lat': lat,
            'lng': lng,
            'Population': pop
        })
        shape_dict.update({
            'PC4': ID,
            'Population': pop,
            'Shape': shape
        })
        
        pop_rows_list.append(pop_dict)
        shape_rows_list.append(shape_dict)
    
    pop_frame = pd.DataFrame(pop_rows_list)
    pop_frame.to_csv(popfile, sep=';', index=False)
    shape_frame = pd.DataFrame(shape_rows_list)
    shape_frame.to_csv(shapefile, sep=';', index=False)

def pc4_shape(shapefile) -> tuple:
    ''' Takes in file containing PC4 ID, Population data and Shape. Shapes may consist of 
    multiPolygons, these get split in different polygons. 
    
    Returns a list of polygons and list of corresponding densities
    '''
    C = []      # list of polygons
    D = []      # list of tuples (pc4, density)
    frame = pd.read_csv(shapefile, sep=';')

    for i, row in frame.iterrows():
        pc4 = row['PC4']
        pop = row['Population']
        shapes = str(row['Shape']).split(', [[')
        area = 0
        temp = []
        
        for s in shapes:
            # Ensure string starts and ends with [[ ]], and no more!
            while s[0] == '[':
                s = s[1:]
            while s[len(s)-1] == ']':
                s = s[:len(s)-1]
            s = '[[' + s + ']]'

            coords = ast.literal_eval(s)
            
            # Correct slight shift in data
            new_coords = []
            offset = (0.0007, -0.0015)
            for cord in coords:
                new_cord = tuple(np.add(np.array(cord), np.array(offset)).tolist())
                new_coords.append(new_cord)

            pgon = Polygon(new_coords)
            temp.append(len(C)) # count how many polygons are added
            C.append(pgon)
            area += pgon.area
        
        # Calculate population density
        density = pop / area
        for t in temp:
            D.append(density)
    return (C, D)

# Obsolete?
def make_pc4_polygonlist(shapefile) -> list:
    shapelist = []
    frame = pd.read_csv(shapefile, sep=';')

    for i, row in frame.iterrows():
        coords = ast.literal_eval(row['Shape'])
        pgon = Polygon(coords)
        shapelist.append(pgon)
    return shapelist

def give_coord_list(region: list, vertex_file: str) -> list:
    coords = []             # list of tuples
    vertex_frame = pd.read_csv(vertex_file, index_col='ID', skipinitialspace=True)
    for vID in region:
        if vID == -1:
            return [-1]
        coords.append((vertex_frame.at[vID, 'lat'], 
                       vertex_frame.at[vID, 'lng']))

    return coords

def make_vor_polygonlist(region_file, vertex_file, points_file) -> list:
    shapelist = []
    region_frame = pd.read_csv(region_file, sep=';', index_col='ID ', skipinitialspace=True)
    vertex_frame = pd.read_csv(vertex_file, index_col='ID', skipinitialspace=True)
    points_frame = pd.read_csv(points_file, index_col='ID', skipinitialspace=True)

    for i, row in points_frame.iterrows():
        region = int(row['region'])
        reg_list = ast.literal_eval(str(region_frame.at[region, 'Vertices']))
        coords = give_coord_list(reg_list, vertex_file)
        if coords == [-1]:
            continue
        shapelist.append(Polygon(coords))
    
    return shapelist

def find_intersections(A: list, B: list) -> dict: 
    """Function that finds pairwise intersections of two sets of polygons.
    Returns dict C
    
    Parameters
    --------
    A : list of shapely Polygons
    B : same as A
    C : dictionary linking parent pair to polygon
        { (a, b) : Polygon }
    """
    C = {}

    foo = 0
    for a in A:
        bar = 0
        for b in B:
            inter = a.intersection(b)
            if not inter.is_empty:
                new_key = (foo, bar)
                new_value = inter
                if C.get(new_key) != None:
                    print(f'Key {new_key} is not new!')
                    continue
                C[new_key] = new_value
            bar += 1
        foo += 1
    
    return C

def vor_pop(intersections: dict, densities: list, vor_in: str, vor_out: str):
    ''' Function that finds population for all voronoi regions
    - loop over intersections, calculating surface area, assigning population based on parent pc4
    intersection population is added to parent vor total

    final voronoi file is written containing
     - ID (based on bus stops), Population, lat, lng
    '''

    vor_frame = pd.read_csv(vor_in, index_col='ID', skipinitialspace=True)
    populations = []
    for v in vor_frame.iterrows():
        populations.append(0)

    for tup, poly in intersections.items():
        area = poly.area
        (pc4_parent, vor_parent) = tup
        pop = area * densities[pc4_parent]
        populations[vor_parent] += round(pop)
    
    vor_frame.insert(len(vor_frame.columns)-1, 'Population', populations)
    vor_frame.to_csv(vor_out, sep=';')

    
    

def ignore():
    ''' Bugfixing stuff that would be really annoying to type again. Can be ignored
    '''
    # print all regions in pc4list
    pc4_list= []
    for p in pc4_list:
        fig, ax = plt.subplots()
        img = plt.imread('./Imaging/Images/pc4_cropped.png')
        #ax.imshow(img, extent=(4.435435, 4.550754, 52.116441, 52.18667))
        ax.imshow(img, extent=(4.435435, 4.550754, 52.116441, 52.18667))
        plot = plot_polygon(p)
        plt.ylim(52.1195913, 52.18385562)
        plt.xlim(4.439670482, 4.52402989)
        plt.show()


def main():
    #pc4_region(known_population_file, pc4_pop_output, pc4_shape_output)
    
    # Find intersections        ====================================================================
    pc4_list, pc4_densities = pc4_shape(pc4_shape_output)
    vor_list = make_vor_polygonlist(vor_region_file, vor_vertex_file, vor_points_file)
    intersections = find_intersections(pc4_list, vor_list)
    
    vor_pop(intersections, pc4_densities, vor_points_file, vor_pop_output)


    pass
main()