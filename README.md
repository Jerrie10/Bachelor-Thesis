# Bachelor Thesis Program

This repository contains all data and programs used for my Bachelor Thesis.

Most scripts are taken from [this](https://github.com/adam-rumpf/social-transit) GitHub page by Adam Rumpf. He made a C++ program to make health services in Chicago more accessible by bus. I'm trying to apply his method to the health services in Leiden.

# General Idea

The goal of making health services more accessible by bus is reached by changing the number of busses assigned to each bus line. This has a direct effect on the frequencies each bus stop is serviced, thus having an effect on the waiting times between transfers. Because the amount of people using busses to travel to their health service is small relative to the overall amount of people using the bus for commuting, a constraint is added to limit the extra travel time for the general population. The C++ program uses a hybrid between Tabu- and Simulated anealing local search algorithms.

# Preprocessing

The C++ script uses certain inputfiles to work correctly. We will construct these files by using a python script called `preprocessing.py`. This file condenses the input data to be only the usefull parts. As the bulk of the code is taken from Adam Rumpf, the explantation of the code and the ouline of the input files can be found [here](https://github.com/adam-rumpf/social-transit-solver). All input files should be put in a `data/` folder. Most datafiles contain ID's to identify their entries, these are assumed to be consecutive numbers starting at `0`.

# Transit Solver - Single

After running the python script, a certain number of files wille be created. These are usefull, but not formatted in a way that is instantly readable. Just like the input files, the structure of the output files is explained [here](https://github.com/adam-rumpf/social-transit-solver).

The `social-transit-solver-single` program gives the current flow distribution of the network, as well as the objective values of the current schedule. Regions can be compared based on how accessible health services are when starting a journey in a given region.

## Input files

This program reads input files from a local `data/` folder. The following data files should be included in this folder:

- `arc_data.txt`
- `assignment_data.txt`
- `node_data.txt`
- `objective_data.txt`
- `od_data.txt`
- `problem_data.txt`
- `transit_data.txt`
- `user_cost_data.txt`
- `vehicle_data.txt`

## Output files

This program writes output files to a local `output/` folder. The following files are produced:

- `gravity_metrics.txt`: A full listing of the gravity access metrics of all population centers for the initial solution vector. This is meant for comparing the initial and final results on a center-by-center basis.
- `initial_solution_log.txt`: An initial version of the solution log file for the main solver. Formatted correctly for the main solver, and contains a single row which logs the initial solution along with its constriant and objective values.
- `initial_flows.txt`: The flow vector produced by the nonlinear assignment model for the initial fleet size vector. Includes core arcs only. This file is also used to allow the assignment process to be halted (using `[Ctrl]+[C]`) and resumed. If present it is used as an initial flow vector to speed up the assignment model. It is updated during each iteration of the assignment model's Frank-Wolfe algorithm.
- `user_cost_data.txt`: A copy of the `user_cost_data.txt` input file with the initial user cost filled in based on the results of the single run.

# Transit Solver

The `social-transit-solver` uses the initial values given by the `preprocessing` and `social-transit-solver-single` scripts to find a more optimal solution. The objective values are also given. This can then be compared to the initial values to see if large improvements to the bus schedule can be made.

## Input files

This program reads input files from a local `data/` folder. The following data files should be included in this folder:

### From Transit solver - single `data/` folder

- `arc_data.txt`
- `assignment_data.txt`
- `node_data.txt`
- `objective_data.txt`
- `od_data.txt`
- `problem_data.txt`
- `transit_data.txt`
- `vehicle_data.txt`

### From Transit solver - single `output/` folder

- `initial_flows.txt`
- `initial_solution_log.txt`
- `user_cost_data.txt`

### New files

- `search_parameters.txt`

# Output files

This program writes outputs to a local `log/` folder. The following files are produced:

- `event.txt`: A log giving a summary of the events during each iteration of the solution process. See below for details.
- `final.txt`: Includes the best known solution vector along with its objective value.
- `memory.txt`: The memory structures associated with the tabu search/simulated annealing hybrid search process. Used to continue a halted search process. Not meant meant to be easily interpreted, but details are included below just in case.
- `metrics.txt`: Accessibility metrics of each population center for the best known solution.
- `solution.txt`: Log of all previously-searched solutions along with their feasibility status, constraint function elements, objective values, and evaluation times. Used to maintain a solution dictionary in order to avoid having to process searched solutions a second time. Its format is the same as that of the input file `initial_solution_log.txt`, but due to the unordered map used to store solutions internally during execution the order of the rows is arbitrary and may change between executions.

The program also prints to the command line as it runs in order to report the main algorithm iteration number and other major events. During the neighborhood search, which is the most time-consuming part of the process, it prints a sequence of characters as an indication that it is still working (specifically, it prints `|` when starting or restarting the first pass, `a` whenever considering a new ADD move during the first pass, `d` for a DROP move, `*` when beginning a constraint calculation, and `.` for each iteration of Frank-Wolfe during constraint calculation).
