cmake_minimum_required(VERSION 3.20)
project(MyProject)

# Zet C++ standaard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Voeg alle source files toe
set(SOURCES
    assignment.cpp
    driver.cpp
    network.cpp
    objective.cpp
    constraints.cpp
)

# Maak executable
add_executable(driver ${SOURCES})
