import numpy as np
import pandas as pd
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import os
import networkx as nx

""" Program that can make illustrations of the multiple graphs 
and maps
"""


# Bushaltes -----------------------------------------------------------------------
class Bushalte:
    instanties = []
    
    def __init__(self, x: float, y: float, name: str, id: int):
        self.naam = name
        self.ID = id
        self.lijnen = [] # buslijnen appenden bij het maken van de lijn
        self.plek = (x,y)
        Bushalte.instanties.append(self)
    
    def __str__(self):
        return f"{self.naam}"
    
    def __repr__(self):  
        return self.__str__()

def zoek_bushalte(id: int) -> Bushalte:
    #plek = alle_bushaltes[naam]
    #halte = arr[plek[0], plek[1]]
    halte = next((obj for obj in Bushalte.instanties if obj.ID == id), None)
    return halte

def maak_bushalte(x: float, y: float, naam: str, id: int):
    halte = Bushalte(x, y, naam, id)

# CSV bestand voor plaatsen van bushaltes importeren
def import_haltes():
    df = pd.read_csv("Rawdata/busstops.csv", sep=';')
    for i, row in df.iterrows():
        maak_bushalte(float(row['lng'].replace(",", ".")), 
                        float(row['lat'].replace(",", ".")),
                        row['Halte'],
                        row['ID'])
                    

# Buslijnen -----------------------------------------------------------------------
class Buslijn:
    instanties = []

    def __init__(self, ID: int, name: str, haltes: dict): 
        'Old functionality: , frequentie: int, starttijd: int'
        self.naam = name
        self.id = ID
        '''
        self.starttijd = starttijd
        self.frequentie = frequentie
        '''
        self.haltes = haltes
        self.color = tuple(np.random.random(size=3))
        Buslijn.instanties.append(self)

    def __str__(self):
        return self.naam
    
    def __repr__(self):  
        return self.__str__()
    
    # nog nodig?
    def volgende(self, halte) -> Bushalte:
        lijst = iter(self.haltes)
        for punt in lijst:
            if punt == halte:
                volg = next(lijst, None)
                break
        return volg


def import_busrit(csv_bestand, naam_buslijn: str) -> dict:
    # CSV bestand voor rit van één buslijn importeren
    haltes = {}
    df = pd.read_csv(csv_bestand)
    df.columns = df.columns.str.strip() #spaties en tabs wegwerken
    for row in df.itertuples():
        if row.Buslijn == naam_buslijn:
            haltes[row.Bushalte] = row.TijdTotVolgende
    return haltes

def import_lijnen(csv_bestand):
    # CSV bestand met alle buslijnen importeren
    routes = {}
    routes_df = pd.read_csv(csv_bestand)
    for i, row in routes_df.iterrows():
        if row['route_ID'] not in routes.keys():
            routes[row['route_ID']] = {}
        routes[row['route_ID']][row['StopID']] =row['traveltime to next stop']

    lijnen_df = pd.read_csv("Rawdata/routes.csv", sep=';')
    for i, row in lijnen_df.iterrows():
        ID = row['ID']
        lijn = Buslijn(ID, row['name'], routes[ID])
        for halteID in routes[ID].keys(): 
            halte = zoek_bushalte(halteID)
            halte.lijnen.append(lijn)

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

def get_coords_csv(file: str) -> list:
    """ Converts csv file to list of coordinates, needs csv file
    with , separator and columns named 'lat', 'lng'
    """
    filename, file_extension = os.path.splitext(file)
    if (file_extension) != ".csv":
        print(f"{file} is not a csv file!")
        return -1
    
    coords = []
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
    busstop_coords = get_coords("RawData/busstops.csv")
    
    img = plt.imread('Images/pc4_cropped.png')
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[4.435435, 4.550754, 52.116441, 52.18667])
    forceAspect(ax)

    points = np.array(busstop_coords)
    vor = Voronoi(points)
    voronoi_plot_2d(vor, point_size=10, ax=ax, show_vertices =False)
    plt.show()

def draw_gp():
    """ Draws the locations of the different GP practices on a map of Leiden"""
    health_coords = get_coords_csv("Intermediate/healthdata.csv")
    img = plt.imread("Images/Gemeente_Leiden.png")
    fig, ax = plt.subplots()
    ax.set_xlim([4.42753, 4.53527])
    ax.set_ylim([52.11850, 52.18488])
    ax.imshow(img, extent=[4.42753, 4.53527, 52.11850, 52.18488])
    forceAspect(ax)
    
    

    points = np.array(health_coords)
    ax.scatter(points[:, 0], points[:, 1])
    plt.show()

# -------------------------------------------------------------------------------------------------
def make_graph() -> nx.Graph:
    G = nx.MultiDiGraph() # Directed graph, allowing multiple arrows between vertices
    for h in Bushalte.instanties:
        G.add_node(h, name=h.naam)
    for lijn in Buslijn.instanties:
        halte_namen = list(lijn.haltes.keys()) 
        a = zoek_bushalte(halte_namen[0])
        for i in range(1, len(halte_namen)):
            b = zoek_bushalte(halte_namen[i])
            gewicht = lijn.haltes[halte_namen[i-1]]
            G.add_edge(a, b, weight= gewicht, color=lijn.color)
            a = b

    
    return G

# -------------------------------------------------------------------------------------------------
def teken_graaf(G: nx.Graph, naam: str):
    # Draw background
    node_pos = {}
    for h in Bushalte.instanties: node_pos.update({h : (h.plek[0], h.plek[1])})

    img = plt.imread('Images/pc4_cropped.png')
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[4.435435, 4.550754, 52.116441, 52.18667]) 
    forceAspect(ax)
    
    
    # Teken knopen
    node_size = 10
    nx.draw_networkx_nodes(G, 
                     pos = node_pos, 
                     node_size = node_size,
                     node_color='k')
    
    # Teken randen 
    edges = list(G.edges(data=True, keys=True))
    con_style = []
    colors = nx.get_edge_attributes(G, 'color').values()
    for i, (u, v, key, data) in enumerate(edges):
        offset = 0.2 * (key + 1)
        con_style.append(f"arc3,rad={offset}")
        #print(f"{(u, v, key)}, Offset: {offset}")
        #data['connectionstyle'] = f'arc3,rad={offset}'
        #print(f"{(u, v, key, data['connectionstyle'])}")
    nx.draw_networkx_edges(G, 
                           node_pos, 
                           arrows=True, 
                           edge_color=colors, 
                           connectionstyle=con_style,
                           arrowstyle='-',
                           node_size= node_size
                            )
    
    plt.savefig(naam + ".png")


# -------------------------------------------------------------------------------------------------
def draw_buslines():
    import_haltes()
    import_lijnen("Intermediate/stopID_times.csv")
    G = make_graph()
    teken_graaf(G, "Images/buslijnen_pc4")

    


# -------------------------------------------------------------------------------------------------
def main():
    #draw_voronoi()
    #draw_buslines()
    draw_gp()
    pass

main()