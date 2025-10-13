# Data for Bachelor Thesis

All data used for my thesis.

## Communities

The files `pc4.csv` and `Voronoi populations.csv` consist of the following columns:

- `ID`: A unique number identifying this row
- `lat`: Latitude of community center
- `lng`: Longitude of community center
- `Population`: Amount of people living in that community

## GP offices `healthdata.csv`

- `Name`: Name of GP-office
- `Amount of doctors`: Number of full-time doctors active at this office, used as quality metric
- `Address`: Address of GP-office, used to get coordinates
- `lat`: Latitude of GP-office
- `lng`: Longitude of GP-office

## Bus-stops `busstops.csv`

- `ID`: A unique number identifying this row
- `Stop name`: Name of bus-stop
- `lat`: Latitude of bus-stop
- `lng`: Longitude of bus-stop

## Travel data `OD data.csv`

File contains listlike representation of OD-matrix. Each row represents one directed arc and its travel-volume over the entire time horizon.

- `ID`: A unique number identifying this row
- `Origin`: Bus-stop ID of origin node

* `Destination`: Bus-stop ID of destination node
* `Volume`: Travel volume over entire time horizon

## `routes.csv`

- `ID`: A unique number identifying this row
- `name`: Name of this route
- `frequency`: Service frequency of this line in starting solution

Note that frequency does not equal number of allocated vehicles, which is derived from frequency, time needed for a round trip and time horizon.

## `route_times.csv`

Ordered list of all stops made by all lines.

- `route_ID`: Corresponds to `routes.csv`
- `name`: Corresponds to `routes.csv`
- `bus_stop`: Bus-stop corresponding to this row
- `traveltime to next stop`: Planned time in minutes to next stop, can be 0 when stops are nearby.
