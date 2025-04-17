# Bachelor Thesis Program

This repository contains all data and programs used for my Bachelor Thesis.

Most scripts are taken from [this](https://github.com/adam-rumpf/social-transit) GitHub page by Adam Rumpf. He made a C++ program to make health services in Chicago more accessible by bus. I'm trying to apply his method to the health services in Leiden.

To do this, GTFS data about bus travel in the Netherlands is included. Scripts that weed out data that is irrelevent for my scope are going to be made and included.

_Currently, the GTFS files are to large to upload to GitHub, so will need to be processed locally. The script included will be written to work on general GTFS files taken from [this website](https://gtfs.ovapi.nl/nl/)._

# General Idea

The goal of making health services more accessible by bus is reached by changing the number of busses assigned to each bus line. This has a direct effect on the frequencies each bus stop is serviced, thus having an effect on the waiting times between transfers. Because the amount of people using busses to travel to their health service is small relative to the overall amount of people using the bus for commuting, a constraint is added to limit the extra travel time for the general population. The C++ program uses a hybrid between Tabu- and Simulated anealing local search algorithms. 

# Input files

The C++ script uses certain inputfiles to work correctly. We will construct these files by using a python script called `preprocessing.py`. This file condenses the GTFS data to be only the usefull parts. As the bulk of the code is taken from Adam Rumpf, the explantation of the code and the ouline of the input files can be found [here](https://github.com/adam-rumpf/social-transit-solver). 

## GTFS data

As mentioned before, the GTFS data on bus travel in the Netherlands is too large to be included. An example dataset is included in this repository to illustrate how the raw data is formatted. This dataset is created by trimming the large files and only keeping the first ~400 lines of data. The arbitrary deletion of data will probably make this dataset not functional, because routes, lines, trips, and bus-stops can not be cross-refferenced between files. It is solely included to get a vague understanding of the raw data that is used. Below is a short overview of what each file is used for, the official documentation of general GTFS data can be found [here](https://gtfs.org/documentation/schedule/reference/). 

###  `agency`

Lists all transit agencies that are included in the dataset. In Leiden there are two bus agencies: EBS and Qbuzz. EBS runs regional routes between cities and has a couple stops in Leiden, Qbuzz also runs regional busses, but has special lines that are completely contained within Leiden.

###  `calendar_dates`

Lists dates where bus service is different, like national holidays or during maintenance. As we are concerned with general planning, this file is omitted later.

###  `feed_info`

Contains information about the dataset, like the author and where it was found.

###  `routes`

Lists all routes, with certain properties like operating agency, route name and route color.

###  `shapes`

Lists all shapes a route can take. A shape consist of a series of points that are connected by straight lines. The order in which the points are entered in the file is the order of travel.

###  `stops`

Lists all bus stops with their ID, name and other properties. Exact location via coordinates is included. 

###  `transfers`

Connects stops or trips when transfers are possible, can give minimum transfer time for a given transfer.

###  `trips`

Lists all trips. Note that a route may be serviced multiple times a day, giving multiple unique trips. Contains direction and shape of trip, among other properties.


# Output files

After running the script, a certain number of files wille be created. These are usefull, but not formatted in a way that is instantly readable. Just like the input files, the structure of the output files is explained [here](https://github.com/adam-rumpf/social-transit-solver). 

## What can be learned?

The `social-transit-solver-single` program gives the current flow distribution of the network, as well as the objective values of the current schedule. Regions can be compared based on how accessible health services are when starting a journey in a given region. 

The `social-transit-solver` uses the initial values given by the `preprocessing` and `social-transit-solver-single` scripts to find a more optimal solution. The objective values are also given. This can then be compared to the initial values to see if large improvements to the bus schedule can be made.
