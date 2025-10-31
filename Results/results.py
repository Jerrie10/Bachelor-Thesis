''' Program that uses results of Transit Solver and maken figures to display those results

'''

import numpy as np
import pandas as pd
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import networkx as nx

pc4_header = './Results/pc4, halffull/'
vor_header = './Results/vor, halffull K=25/'

pc4_id = [2311, 2312, 2313, 2314, 2315, 2316, 2317, 2318, 
          2321, 2322, 2323, 2324, 2331, 2332, 2333, 2334]

def solution_line(file_header: str):
    ''' Function that makes a line diagram of the solution of each iteration
    
    Parameters
    ------------
    file_header : string, one of 
    - './Results/pc4, halffull/'
    - './Results/vor, halffull K=25/'
    '''
    colors = ['mediumseagreen', 'mediumvioletred']
    i = 0
    if file_header[10:13] == 'vor':
        i = 1

    file = file_header + '/log1/event.txt'
    events = pd.read_csv(file, sep='\t')
    cur_values = -events['Obj_Current']
    opt_values = -events['Obj_Best']

    ymin = cur_values.min()
    ymax = cur_values.max()
    
    cur_line, = plt.plot(cur_values, c=colors[i], label='Current Solution', linewidth=.5)
    opt_line, = plt.plot(opt_values, c=colors[i], label='Best known Solution', linestyle='dotted')
    
    plt.xlabel('Iterations')
    plt.ylabel('Accesibility')
    plt.axis((-20, 500, ymin*0.95, ymax*1.01))
    plt.legend(handles=[cur_line, opt_line], loc='lower right')
    
    #plt.show()
    plt.savefig(file_header + file_header[10:13] + '_objectivevalue', bbox_inches = 'tight')

def accesibility_table(file_header: str, columns=1):
    ''' Function that makes some tables from the accesibility metrics, formatted to be copy-pasted 
    in a LaTeX file
    
    Tables produced are 'All results' and 'Descriptions'
    
    All results : a row for each community area, columns are
    - Initial value
    - Final value
    - Absolute difference
    - Relative difference
    
    Descriptions 
    - Rows 
        - Std. Dev
        - Variance
        - Median
        - Min
        - Max
    - Columns
        - Initial
        - Final
        - Abs. Diff
        - Rel. Diff

    Parameters
    -----------
    file_header : path to folder with relevant files, also used as location of output files

    columns : optional variable, determines how many 
    '''

    # Make dataframe containing initial and final values
    init = pd.read_csv(file_header + 'gravity_metrics.txt', 
                       sep='\t', header=0,
                       names=['Initial'])
    final = pd.read_csv(file_header + '/log1/metrics.txt', 
                        sep='\t', header=0, 
                        names=['Final'])
    results = pd.concat([init, final], axis=1)

    # Write all results to file
    all_results_file = file_header + file_header[10:13] + '_all_results.txt'
    all_results_list = [] 
    for i, row in results.iterrows():
        id =  i      #pc4_id[int(str(i)) - 1] 
        foo = row['Initial']
        bar = row['Final']
        abs_diff = bar - foo
        rel_diff = round((abs_diff / foo) * 100, 1)
        res1 = str(id) + '&' + '{:.5e}'.format(foo) + '&' + '{:.5e}'.format(bar) + '&' 
        res2 = '{:.5e}'.format(abs_diff) + '&' + str(rel_diff) +'\\%'
        all_results_list.append(res1 + res2) 
    
    with open(all_results_file, 'w') as fout:
        for line in all_results_list:
            print(line + '\\\\', file=fout)
            # TODO: rework zodat columns slim worden gedaan

    # Calculate descriptions and write to file
    descriptions_file = file_header + file_header[10:13] + '_descriptions.txt'
    
    description = results.describe(percentiles=[])
    description = description.drop(index=['count', '50%'])
    descriptions_list = []
    
    
    for i, row in description.iterrows():
        id = i
        foo = row['Initial']
        bar = row['Final']
        abs_diff = bar - foo
        rel_diff = round((abs_diff / foo) * 100, 1)
        res1 = str(id) + '&' + '{:.5e}'.format(foo) + '&' + '{:.5e}'.format(bar) + '&' 
        res2 = '{:.5e}'.format(abs_diff) + '&' + str(rel_diff) +'\\%'
        descriptions_list.append(res1 + res2)

    with open(descriptions_file, 'w') as fout:
        for line in descriptions_list:
            print(line + '\\\\', file=fout)
            # TODO: rework zodat columns slim worden gedaan

def main():    
    #solution_line(vor_header)
    accesibility_table(vor_header)

    pass
main()