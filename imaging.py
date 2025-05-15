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
    df = pd.read_csv(csv_bestand)
    for i, row in df.iterrows():
        if row['route_ID'] not in routes.keys():
            routes[row['route_ID']] = {}
        routes[row['route_ID']][row['StopID']] =row['traveltime to next stop']

    for lijnID in routes.keys():
        lijn = Buslijn(row['route_ID'], row['name'], routes[lijnID])
        for halteID in routes[lijnID].keys(): 
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
            G.add_edge(a, b, weight= gewicht)
            a = b

    return G

# -------------------------------------------------------------------------------------------------
def teken_graaf(G: nx.Graph, naam: str):
    img = plt.imread('Images/pc4_cropped.png')
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[4.435435, 4.55486, 52.116441, 52.18667])
    forceAspect(ax)
    
    node_pos = {}
    for h in Bushalte.instanties: node_pos.update({h : (h.plek[0], h.plek[1])})

    # Teken knopen
    nx.draw_networkx_nodes(G, 
                     pos = node_pos, 
                     node_size = 20)
    
    # Teken randen 
    nx.draw_networkx_edges(G, node_pos, arrows=False)
    
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
    
    pass

main()