
import warnings
warnings.filterwarnings('ignore') # hopefully stop any pedantic warnings

import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = (12.0, 12.0) # set default size of plots
plt.rcParams['image.interpolation'] = 'nearest'

import os
import sys
from tree_genotype import *
from selection import *
from gpac_population_evaluation import *
from genetic_programming import *
from base_evolution import *
from search_runner import genetic_programming_search, run_and_log
from multiprocessing import Pool



if __name__ == '__main__':
    number = sys.argv[1]
    # Feel free to change these values and re-run this cell as much as you'd like
    number_runs = 8
    number_evaluations = 5000
    config_filename = f'configs/2b_yellow_config{number}.txt'
    log_directory = f'data/2b/yellow{number}/logs/tuning/'

    os.makedirs(log_directory, exist_ok=True)

    # Tuning runs can be called here
    def one_run(i):
        run_and_log(genetic_programming_search, number_evaluations, config_filename, log_directory+str(i)+".json")

    with Pool() as pool:
        pool.map(one_run, range(number_runs))