# Traveling Salesman Problem Solver

## Introduction
This script solves the Traveling Salesman Problem (TSP) using a branch-and-bound algorithm with depth-first search. It includes a class-based implementation for better organization and reusability.

## Requirements
- Python 3.x

## Installation
No special installation is required. Simply clone or download the repository to your local machine.
```bash
git clone https://github.com/hjimjim/TravelingSalesmanProblem.git
```

## Running the Script
```bash
python3.10 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt

cd src
# for branch and bound
python3 branch_bound_dfs.py

# for sls
python3 stochastic_local_search.py
```

## Where to See Result
Everytime you run python file new folder will be created. 
Created folder names will be as follows.
output/bnbdfs/{date}_{time}
output/sls/{date}_{time}

In each directory you can see intermediate results and total result in each folder created.