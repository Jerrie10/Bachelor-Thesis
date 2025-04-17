# Bachelor Thesis Program

This repository contains all data and programs used for my Bachelor Thesis.

Most scripts are taken from [this](https://github.com/adam-rumpf/social-transit) GitHub page by Adam Rumpf. He made a C++ program to make health services in Chicago more accessible by bus. I'm trying to apply his method to the health services in Leiden.

To do this, GTFS data about bus travel in the Netherlands is included. Scripts that weed out data that is irrelevent for my scope are going to be made and included.

_Currently, the GTFS files are to large to upload to GitHub, so will need to be processed locally. The script included will be written to work on general GTFS files taken from [this website](https://gtfs.ovapi.nl/nl/)._

# Input files

The C++ script uses certain inputfiles to work correctly. We will construct these files by using a python script called `preprocessing.py`. This file condenses the GTFS data to be only the usefull parts. As the bulk of the code is taken from Adam Rumpf, the explantation of the code and the ouline of the input files can be found [here](https://github.com/adam-rumpf/social-transit-solver). 


# Output files

After running the script, a certain number of files wille be created. These are usefull, but not formatted in a way that is instantly readable. Just like the input files, the structure of the output files is explained [here](https://github.com/adam-rumpf/social-transit-solver). 

## What can be learned?

The `social-transit-solver-single` program gives the current flow distribution of the network, as well as the objective values of the current schedule. Regions can be compared based on how accessible health services are when starting a journey in a given region. 

The `social-transit-solver` uses the initial values given by the `preprocessing` and `social-transit-solver-single` scripts to find a more optimal solution. The objective values are also given. This can then be compared to the initial values to see if large improvements to the bus schedule can be made.
