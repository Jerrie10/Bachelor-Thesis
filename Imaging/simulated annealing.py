import numpy as np
import random
import math
import matplotlib.pyplot as plt


class Cell:
    value = 0
    location = (0,0)

    def __init__(self, value, x, y) -> None:
        self.value = value
        self.location = (x, y)


# Global variables      ============================================================================
grid = [
    [ 10, 3, 5, 8, 9],
    [ 1, 3, 3, 6, 3],
    [ 3, 5, 4, 3, 3],
    [ 1, 3, 1, 7, 1],
    [ 1, 2, 1, 2, 6],
]

startpoint = (4,0)      # Lower left
T_start = 10                # Starting Temp
T_end = 0.5             # Ending Temp
alpha = 0.95            # Cooling multiplier



def select_neighbor(point: tuple) -> tuple:
    ''' Function that takes in a point in the grid and picks a random neighbor'''
    (x_p, y_p) = point
    Nx = [x_p]
    Ny = [y_p]
    # Find N(s)
    if (x_p > 0):
        Nx.append(x_p - 1)
    if (x_p < 4):
        Nx.append(x_p + 1)

    if (y_p > 0):
        Ny.append(y_p - 1)
    if (y_p < 4):
        Ny.append(y_p + 1)

    neighborhood = []
    for x in Nx:
        for y in Ny:
            if x == x_p and y == y_p:
                continue
            neighborhood.append((x, y))
    
    randomnumber = random.randint(0, len(neighborhood)-1)
    # Pick random
    neighbor = neighborhood[randomnumber]
    return neighbor


def print_points(points: list):
    output_file = './Imaging/simulated annealing.txt'
    u = (-1, -1)
    output = '\\draw '
    with open(output_file, 'a') as fout:
        for v in points:
            if u == v:
                continue
            if u == (-1, -1):
                u = v
                continue
            #print(f'\\draw[arrow] (c{u[1]+1}{u[0]+1}) -- (c{v[1]+1}{v[0]+1});', file=fout)
            output += f'-- (c{v[1]+1}{v[0]+1})'
            u=v
        output += ';'
        print(output, file=fout)

def sim_annealing():
    temp= T_start
    current_point = startpoint
    points_to_print = [current_point]           # For printing
    while temp > T_end:
        # Do iteration
        neighbor = select_neighbor(current_point)
        delta = grid[neighbor[0]][neighbor[1]] - grid[current_point[0]][current_point[1]]

        if delta > 0:
            current_point = neighbor
        else:
            randomnumber = random.random()
            if randomnumber < math.e**(delta/temp):
                current_point = neighbor

        # Cool
        temp = temp*alpha

        #Print results
        points_to_print.append(current_point)
    print_points(points_to_print)


def main():
    for i in range(10):
        sim_annealing()   

    pass

main()