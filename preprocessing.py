import numpy as np
import geopy.distance as gpd
import pandas as pd
import requests
import json


#==============================================================================
# Parameters
#==============================================================================

# Raw Data input/output files
population_clustered = "RawData/pc4.csv"
facility_raw = "RawData/healthlocations.csv"
facility_in = "Intermediate/healthdata.csv"
facility_out = "Intermediate/facility.csv"

stop_data = "RawData/busstops.csv"
time_data = "RawData/route_times.csv"
route_data = "RawData/routes.csv"
route_times = "Intermediate/stopID_times.csv"

line_nodes = "Intermediate/line_nodes.txt"
line_arcs = "Intermediate/line_arcs.txt"


# Output network file parameters
nid_stop = 0 # stop node type
nid_board = 1 # boarding node type
nid_pop = 2 # population center node type
nid_fac = 3 # primary care facility node type
aid_line = 0 # line arc type
aid_board = 1 # boarding arc type
aid_alight = 2 # alighting arc type
aid_walk = 3 # standard walking arc type
aid_walk_health = 4 # walking arc type to connect pop centers and facilities
final_arc_data = "Data/arc_data.txt"
final_node_data = "Data/node_data.txt"
final_transit_data = "Data/transit_data.txt"
km_walk_time = 60/4  # minutes to walk 1km when walking 4km/h


# Misc. data


#==============================================================================
# Functions
#==============================================================================

def address_to_coords(inputfile, outputfile):
    """Uses the MapQuestAPI to get coordinates of locations, based on adress
    """
    private = json.load(open("private.json", 'r'))
    api_key = private['MapQuest']
    
    df = pd.read_csv(inputfile, sep=';')
    pd.set_option('display.max_rows', None)

    for i, row in df.iterrows():
        apiAddress = str(df.at[i,'Adres'])
        
        parameters = {
            "key": api_key,
            "location": apiAddress
        }

        response = requests.get("http://www.mapquestapi.com/geocoding/v1/address", params=parameters)
        
        data = response.text
        dataJ = json.loads(data)['results']
        lat = (dataJ[0]['locations'][0]['latLng']['lat'])
        lng = (dataJ[0]['locations'][0]['latLng']['lng'])
        
        df.at[i,'lat'] = lat
        df.at[i,'lng'] = lng
        
    df.to_csv(outputfile, index= False)

def distance(x, y, taxicab=False):
    """Calculates geodesic distance (km) between two tuples of coordinates.

    Accepts an optional argument indicating whether to use taxicab distance
    instead of the default Euclidean distance.
    """

    if taxicab == False:
        return gpd.geodesic(x, y).km
    else:
        return min(gpd.geodesic(x, (x[0],y[1])).km +
                   gpd.geodesic((x[0],y[1]), y).km, gpd.geodesic(x,
                               (y[0],x[1])).km + gpd.geodesic((y[0],x[1]),
                               y).km)

# -------------------------------------------------------------------------------------------------
def facility_processing(input_file, output_file):
    df = pd.read_csv(input_file)
    df = df[["Name", "lat", "lng"]]
    df.to_csv(output_file, index= False)

# -------------------------------------------------------------------------------------------------
def stop_processing(stop_file, raw_times, processed_times):
    """ Adds stop ID's to route time file
    """
    
    # Make dictionary of stops, "Name" : ID
    stops = {}
    stop_df = pd.read_csv(stop_file, sep=';')
    for i, row in stop_df.iterrows():
        stops[row['Halte']] = row['ID']

    # Add stop ID to each row of route times
    df = pd.read_csv(raw_times, sep=';')
    stop_id = []
    for i, row in df.iterrows():
        stop_name = row['bus_stop']
        stop_id.append(stops[stop_name])
    
    df.insert(3, "StopID", stop_id, True)

    df.to_csv(processed_times, index= False)
    pass

# -------------------------------------------------------------------------------------------------
def transit_processing(stop_file, route_file, stop_time_file,
                       node_output_file, arc_output_file):
    """Preprocessing for transit network data.

    Requires the following file names (respectively): GTFS stop data, GTFS trip
    data, GTFS route data, GTFS stop time data, output file for node list,
    output file for arc list, and output file for line info.

    
    The node and arc output files treat the cluster IDs as the stop node IDs,
    and include the boarding nodes, boarding arcs, alighting arcs, and line
    arcs for each line, along with the correct base travel times.
    """

    nodenum = -1 # current node ID
    arcnum = -1 # current arc ID

    # Write header for arc file
    with open(arc_output_file, 'w') as f:
        print("ID\tType\tLine\tTail\tHead\tTime", file=f)

    # Dictionary linking stop ID to coordinates
    stops = {}

    # Read cluster file while writing the initial node file
    with open(node_output_file, 'w') as fout:
        print("ID\tName\tType\tLine", file=fout)
        
        with open(stop_file, 'r') as fin:
            i = -1
            for line in fin:
                i += 1
                if i > 0:
                    # Skip comment line
                    dum = line.split(sep=';')
                    stops[int(dum[0])] = [float(dum[2].replace(',', '.')), float(dum[3].replace(',', '.'))]
                    if int(dum[0]) > nodenum:
                        nodenum = int(dum[0])
                    print(str(nodenum)+"\tStop"+str(nodenum)+"\t"+
                          str(nid_stop)+"\t-1", file=fout)
    
    # Create list of all routes
    routes = []
    with open(route_file, 'r') as f:
        i = -1
        for line in f:
            i += 1
            if i > 0:
                # Skip comment line
                dum = line.split(';')
                routes.append(int(dum[0]))
    
    # Collect stops for each route
    stoptimes_frame = pd.read_csv(stop_time_file)

    for r in routes: 

        # Initialize dict for each route, stopID: next traveltime
        # Still needed?
        route_stops = {}
        for i, row in stoptimes_frame.iterrows():
            if (int(row['route_ID']) == r):
                route_stops[row['StopID']] = row['traveltime to next stop']
        
        
        # Initialize weighted arc list. (u, v) : traveltime
        arcs = {}
        u = -1
        time = -1
        for i, row in stoptimes_frame.iterrows():
            if (int(row['route_ID']) == r):
                v = row['StopID']
                if (u > -1):
                    arcs[(u,v)] = time
                u = v
                time = row['traveltime to next stop']
        #print(arcs)
        
        # Create boarding nodes and arcs
        boarding = {}
        for u in stops:
            if(u in boarding) == False:
                nodenum += 1
                boarding[u] = nodenum

        # Add boarding nodes to file
        with open(node_output_file, 'a') as f:
            for u in boarding:
                # ID, Name, Type, Line
                print(str(boarding[u])+"\tStop"+str(u)+"_Route"+str(r)+
                      "\t"+str(nid_board)+"\t"+str(r), file=f)
                

        # Add arcs to arc file
        with open(arc_output_file, 'a') as f:
            # Line arcs
            for a in arcs:
                # ID, Type, Line, Tail, Head, Time
                arcnum += 1
                print(str(arcnum)+"\t"+str(aid_line)+"\t"+str(r)+"\t"+
                      str(boarding[a[0]])+"\t"+str(boarding[a[1]])+"\t"+
                      str(arcs[a]), file=f)

            # Boarding arcs
            for u in stops:
                arcnum += 1
                print(str(arcnum)+"\t"+str(aid_board)+"\t"+str(r)+"\t"+
                      str(u)+"\t"+str(boarding[u])+"\t0", file=f)

            # Alighting arcs
            for u in stops:
                arcnum += 1
                print(str(arcnum)+"\t"+str(aid_alight)+"\t"+str(r)+"\t"+
                      str(boarding[u])+"\t"+str(u)+"\t0", file=f)

        print("Done processing route "+str(r))

# -------------------------------------------------------------------------------------------------
def add_walking(stop_file, arc_file, cutoff = 0.25):
    """Generates walking arcs between stops.

    Requires the name of the arc file and the stop file.

    Accepts an optional keyword argument to specify the (taxicab) distance
    cutoff (km), within which walking arcs will be generated.

    Clusters within the cutoff distance of each other will receive a pair of
    walking arcs between them, with a travel time calculated based on the
    distance and the walking speed defined above.

    #In order to reduce the number of arcs in densely-packed clusters of stops,
    we prevent arcs from being generated between pairs of stops if the
    quadrangle defined by them contains another stop.
    """
    ids = []
    coords = []
    df = pd.read_csv(stop_file, sep=';')
    for i, row in df.iterrows():
        ids.append(row['ID'])
        coords.append((row['lat'].replace(',', '.'), row['lng'].replace(',', '.')))

    # Go through each unique coordinate pair and generate a dictionary of pairs
    # within the cutoff distance of each other
    count = 0
    pairs = {}
    for i in range(len(coords)):
        print("Iteration "+str(i+1)+" / "+str(len(coords)))

        for j in range(i):
            # Calculate pairwise distance
            dist = distance(coords[i], coords[j], taxicab=True)
            if dist <= cutoff:
                keep = True # whether to keep the current pair

                # Define corners of quadrangle as most extreme lat/lon in pair
                lat_min = min(coords[i][0], coords[j][0])
                lat_max = max(coords[i][0], coords[j][0])
                lon_min = min(coords[i][1], coords[j][1])
                lon_max = max(coords[i][1], coords[j][1])

                # Scan entire stop list for stops within the quadrangle
                for k in range(len(coords)):
                    if (k != i) and (k != j):
                        if ((lat_min <= coords[k][0] <= lat_max) and
                            (lon_min <= coords[k][1] <= lon_max)):
                            # Stop found in quadrangle, making pair invalid
                            keep = False
                            break

                # If no stops were found in the quadrangle, then we add the
                # pair along with their walking time to the dictionary
                if keep == True:
                    count += 1
                    pairs[(ids[i], ids[j])] = dist * km_walk_time

    # Use the final pairs dictionary to generate the new arcs and write them to
    # the arc file
    with open(arc_file, 'r+') as f:
        # Count the number of arcs
        arcnum = -np.inf
        f.readline()
        for line in f:
            li = f.readline().split()
            if len(li) > 0:
                # Skip the blank line at the end
                arcnum = max(arcnum, int(li[0]))
        arcnum += 1

        for p in pairs:
            # ID, Type, Line, Tail, Head, Time
            print(str(arcnum)+"\t"+str(aid_walk)+"\t-1\t"+str(p[0])+"\t"+
                  str(p[1])+"\t"+str(pairs[p]), file=f)
            arcnum += 1
            print(str(arcnum)+"\t"+str(aid_walk)+"\t-1\t"+str(p[1])+"\t"+
                  str(p[0])+"\t"+str(pairs[p]), file=f)
            arcnum += 1

    print("Done. Added a total of "+str(count)+" pairs of walking arcs.")



    pass


#TODO ---------------------------------------------------------------------------------------------
#def cluster_boarding   (need user data)
#def gamma              (need user data)
#def all_times          (need user data)
#def od_matrix          (need user data)

# -------------------------------------------------------------------------------------------------
def network_assemble(input_stop_nodes, input_line_arcs, input_pop_nodes,
                     input_fac_nodes, input_stops, output_nodes, output_arcs, cutoff=0.25):
    """Assembles most of the intermediate files into the final network files.

    Requires the following file names in order:
        core network nodes (stops and boarding)
        core network arcs (line, boarding, alighting, and walking)
        population center nodes
        facility nodes
        cluster coordinates
        community area names
        final node output
        final arc output

    Accepts an optional keyword "cutoff" for use in generating walking arcs
    between population centers/facilities/stops. Defaults to 0.5. Represents
    taxicab distance (miles) within wich to generate walking arcs.

    The network assembly process consists mostly of incorporating the
    population centers and facilities into the main network. This is done in
    mostly the same way as the walking arc script, except that each facility
    and population center is guaranteed to receive at least one walking arc,
    which is connected to the nearest stop node if none were within the cutoff.
    """

    # Read in lists of stop IDs and coordinates
    stop_ids = []
    stop_coords = []
    stop_df = pd.read_csv(input_stops, sep=';')
    for i, row in stop_df.iterrows():
        stop_ids.append(row['ID'])
        stop_coords.append((float(row['lat'].replace(',', '.')), 
                            float(row['lng'].replace(',', '.'))))
        
    # Read in dictionaries indexed by population center IDs to contain the
    # population values, center names, and coordinates
    pop_names = {}
    populations = {}
    pop_coords = {}
    pop_df = pd.read_csv(input_pop_nodes, sep=';')
    pop_id = -1
    for i, row in pop_df.iterrows():
        pop_id = pop_id + 1
        populations[pop_id]=int(str(row['Inwoners']).replace('.',''))
        pop_names[pop_id] = row['ID']
        pop_coords[pop_id] =((float(row['lat'].replace(',', '.')), 
                            float(row['lng'].replace(',', '.'))))

    # Go through each population center and generate a dictionary of stop IDs
    # that should be linked to each center
    count = 0
    pop_links = {}
    pop_link_times = {}
    for i in pop_coords:
        print("Population center "+str(i))

        # Continue searching until we find at least one link to add
        effective_cutoff = cutoff
        pop_links[i] = []
        pop_link_times[i] = []
        while len(pop_links[i]) == 0:

            for j in range(len(stop_coords)):
                # Calculate pairwise distance
                dist = distance(pop_coords[i], stop_coords[j], taxicab=True)
                if dist <= effective_cutoff:
                    keep = True # whether to keep the current pair

                    # Define corners of quadrangle
                    lat_min = min(pop_coords[i][0], stop_coords[j][0])
                    lat_max = max(pop_coords[i][0], stop_coords[j][0])
                    lon_min = min(pop_coords[i][1], stop_coords[j][1])
                    lon_max = max(pop_coords[i][1], stop_coords[j][1])

                    # Scan entire stop list for stops within the quadrangle
                    for k in range(len(stop_coords)):
                        if k != j:
                            if ((lat_min <= stop_coords[k][0] <= lat_max) and
                                (lon_min <= stop_coords[k][1] <= lon_max)):
                                # Stop found in quadrangle, making pair invalid
                                keep = False
                                break

                    # If no stops were found in the quadrangle, then we add the
                    # pair along with their walking time to the dictionary
                    if keep == True:
                        count += 1
                        pop_links[i].append(stop_ids[j])
                        pop_link_times[i].append(dist*km_walk_time)

            # Double the effective cutoff in case the search was unsuccessful
            # and must be repeated
            if len(pop_links[i]) == 0:
                effective_cutoff *= 2
                print("No links found. Trying again with cutoff "+
                      str(effective_cutoff))

    print("Adding a total of "+str(count)+" population walking arcs.")

    # Read in lists to contain the facility names, coordinates and quality
    fac_names = []
    fac_coords = []
    fac_qual = []
    fac_df = pd.read_csv(input_fac_nodes)
    for i, row in fac_df.iterrows():
        fac_names.append(row['Name'])
        fac_coords.append((row['lat'], row['lng']))
        fac_qual.append(row['Hoeveelheid artsen'])
    
    # Go through each facility and generate a dictionary of stop IDs that
    # should be linked to each facility
    count = 0
    fac_links = {}
    fac_link_times = {}
    for i in range(len(fac_coords)):
        print("Facility center "+str(i+1)+" / "+str(len(fac_coords)))

        # Continue searching until we find at least one link to add
        effective_cutoff = cutoff
        fac_links[i] = []
        fac_link_times[i] = []
        while len(fac_links[i]) == 0:

            for j in range(len(stop_coords)):
                # Calculate pairwise distance
                dist = distance(fac_coords[i], stop_coords[j], taxicab=True)
                if dist <= effective_cutoff:
                    keep = True # whether to keep the current pair

                    # Define corners of quadrangle
                    lat_min = min(fac_coords[i][0], stop_coords[j][0])
                    lat_max = max(fac_coords[i][0], stop_coords[j][0])
                    lon_min = min(fac_coords[i][1], stop_coords[j][1])
                    lon_max = max(fac_coords[i][1], stop_coords[j][1])

                    # Scan entire stop list for stops within the quadrangle
                    for k in range(len(stop_coords)):
                        if k != j:
                            if ((lat_min <= stop_coords[k][0] <= lat_max) and
                                (lon_min <= stop_coords[k][1] <= lon_max)):
                                # Stop found in quadrangle, making pair invalid
                                keep = False
                                break

                    # If no stops were found in the quadrangle, then we add the
                    # pair along with their walking time to the dictionary
                    if keep == True:
                        count += 1
                        fac_links[i].append(stop_ids[j])
                        fac_link_times[i].append(dist*km_walk_time)

            # Double the effective cutoff in case the search was unsuccessful
            # and must be repeated
            if len(fac_links[i]) == 0:
                effective_cutoff *= 2
                print("No links found. Trying again with cutoff "+
                      str(effective_cutoff))

    print("Adding a total of "+str(count)+" facility walking arcs.")

     # Write new nodes to final output files
    with open(output_nodes, 'w') as fout:
        # Comment line
        print("ID\tName\tType\tLine\tValue", file=fout)

        # Copy old node file contents
        with open(input_stop_nodes, 'r') as fin:
            i = -1
            nodenum = -1
            for line in fin:
                i += 1
                if i > 0:
                    # Skip comment line
                    dum = line.split()
                    # ID, Name, Type, Line
                    if int(dum[0]) > nodenum:
                        nodenum = int(dum[0])
                    print(dum[0]+"\t"+dum[1]+"\t"+dum[2]+"\t"+dum[3]+"\t-1",
                          file=fout)

        # Write population center nodes
        pop_nodes = {}
        for i in pop_names:
            nodenum += 1
            pop_nodes[i] = nodenum
            print(str(nodenum)+"\t"+str(i)+"_"+str(pop_names[i])+"\t"+
                  str(nid_pop)+"\t-1\t"+str(populations[i]), file=fout)

        # Write facility nodes
        fac_nodes = []
        for i in range(len(fac_names)):
            nodenum += 1
            fac_nodes.append(nodenum)
            print(str(nodenum)+"\t"+str(fac_names[i])+"\t"+str(nid_fac)+
                  "\t-1\t"+str(fac_qual[i]), file=fout)
    
    # Write new arcs to output files
    with open(output_arcs, 'w') as fout:
        # Comment line
        print("ID\tType\tLine\tTail\tHead\tTime", file=fout)

        # Copy old arc file contents
        with open(input_line_arcs, 'r') as fin:
            i = -1
            arcnum = -1
            for line in fin:
                i += 1
                if i > 0:
                    # Skip comment line
                    dum = line.split()
                    # ID, Type, Line, Tail, Head, Time
                    if int(dum[0]) > arcnum:
                        arcnum = int(dum[0])
                    print(line.strip(), file=fout)

        # Write population center walking arcs
        for i in pop_links:
            for j in range(len(pop_links[i])):
                arcnum += 1
                print(str(arcnum)+"\t"+str(aid_walk_health)+"\t-1\t"+
                      str(pop_nodes[i])+"\t"+str(pop_links[i][j])+"\t"+
                      str(pop_link_times[i][j]), file=fout)
                arcnum += 1
                print(str(arcnum)+"\t"+str(aid_walk_health)+"\t-1\t"+
                      str(pop_links[i][j])+"\t"+str(pop_nodes[i])+"\t"+
                      str(pop_link_times[i][j]), file=fout)

        # Write facility walking arcs
        for i in fac_links:
            for j in range(len(fac_links[i])):
                arcnum += 1
                print(str(arcnum)+"\t"+str(aid_walk_health)+"\t-1\t"+
                      str(fac_nodes[i])+"\t"+str(fac_links[i][j])+"\t"+
                      str(fac_link_times[i][j]), file=fout)
                arcnum += 1
                print(str(arcnum)+"\t"+str(aid_walk_health)+"\t-1\t"+
                      str(fac_links[i][j])+"\t"+str(fac_nodes[i])+"\t"+
                      str(fac_link_times[i][j]), file=fout)

#TODO ---------------------------------------------------------------------------------------------
#def transit_finalization
#def misc_files
# -------------------------------------------------------------------------------------------------

def main():
    #(un)comment lines based on what needs to be processed-----------------------------------------
    # TODO rerun everything to avoid duplicate arcs/nodes
    #address_to_coords(facility_raw, facility_in)
    #facility_processing(facility_in, facility_out)
    #stop_processing(stop_data, time_data, route_times)
    
    #transit_processing(stop_data, route_data, route_times, line_nodes, line_arcs)
    #add_walking(stop_data, line_arcs)
    
    
    network_assemble(line_nodes, line_arcs, population_clustered, facility_in,
                 stop_data, final_node_data, final_arc_data)
    pass
main()