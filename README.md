# Traveling Salesman Problem Solver

## Introduction
This script solves the Traveling Salesman Problem (TSP) using a branch-and-bound algorithm with depth-first search. It includes a class-based implementation for better organization and reusability.

## Requirements
- Python 3.x

## Installation
python3.10 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt

### Running the Script
```bash
cd src
# for branch and bound
python branch_bound_dfs.py

# for sls
python stochastic_local_search.py
```

### where to see result
After running python file in the output directory we can see intermediate result and total result in each folder created