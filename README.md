# Bachelor Thesis Program

Hello
This repository contains all data and programs used for my Bachelor Thesis.

Most scripts are taken from [this](https://github.com/adam-rumpf/social-transit) GitHub page by Adam Rumpf. He made a C++ program to make health services in Chicago more accessible by bus. I'm trying to apply his method to the health services in Leiden.

To do this, GTFS data about bus travel in the Netherlands is included. Scripts that weed out data that is irrelevent for my scope are going to be made and included.

_Currently, the GTFS files are to large to upload to GitHub, so will need to be processed locally. The script included will be written to work on general GTFS files taken from [this website](https://gtfs.ovapi.nl/nl/)._

# Input files

The C++ script uses certain inputfiles to work correctly. We will construct these files by using a python script called `preprocessing.py`. This file condenses the GTFS data to be only the usefull parts. The input files are structured as follows:

## File 1

## File 2

## ...

# Output files

After running the script, a certain number of files wille be created. These are usefull, but not formatted in a way that is instantly readable. The output files are structured as follows:

## File 1

## File 2

## ...
