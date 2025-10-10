cmake_minimum_required(VERSION 3.20)
project(MyProject)

# Zet C++ standaard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


# Voeg alle source files toe
set(SOURCES
    assignment_nonlinear.cpp
    assignment_constant.cpp
    constraints.cpp
    driver.cpp
    network.cpp
    objective.cpp
    search_common.cpp
    search_evelog.cpp
    search_memlog.cpp
    search_sollog.cpp 
    search.cpp 
)

# Maak executable
add_executable(solver ${SOURCES})
