from typing import Tuple, List
from linear_genotype import LinearGenotype

def load_data_log(filename: str) -> Tuple[int, LinearGenotype, List[int], List[float], List[float], List[int], List[float], List[float]]:
    '''Load the data_log contained in the given filename

    Params:
    -------
    filename: str 

    Returns:
    -------
    A tuple containing, in order,
    best_fitness: The base fitness from the best individual found
    best_individual: The best individual found genes
    evals: a list of eval count at that data point
    penalized_maxes: local max penalized fitness
    penalized_means: local average penalized fitness
    base_maxes: local max base fitness
    base_means: local average base fitness
    valid_proportion: the proportion of valid solutions in the population now
    '''
    # return best_fitness, best_individual, evals, penalized_maxes, penalized_means, base_maxes, base_means
    all_data = []
    best_fitness = -1
    best_individual = LinearGenotype()
    idx = 0

    with open(filename, 'r') as f:
        for line in f:
            idx += 1
            if idx == 1:
                best_fitness = int(line.strip())
            elif idx == 2:
                genes = eval(line.strip())
                best_individual.genes = genes
            else:
                #take off newline char and split it by space
                data = line.strip().split()
                all_data.append(data)

    # Data Log is created like this:
    #{base_ea.evaluations} {local_penalized_fittest} {local_mean_penalized_fitness} {global_base_fittest.fitness} {local_mean_base_fitness}

    evals = [int(x[0]) for x in all_data]
    penalized_maxes = [float(x[1]) for x in all_data]
    penalized_means = [float(x[2]) for x in all_data]
    base_maxes = [int(x[3]) for x in all_data]
    base_means = [float(x[4]) for x in all_data]
    valid_proportion = [float(x[5]) for x in all_data]

    return best_fitness, best_individual, evals, penalized_maxes, penalized_means, base_maxes, base_means, valid_proportion

def load_average_data_logs(filenames: List[str]) -> Tuple[int, LinearGenotype, List[int], List[float], List[float], List[int], List[float], List[float]]:
    '''Load the data_logs from all the filenames, average their data for each column, and return best overall individual

    Params:
    -------
    filename: str 

    Returns:
    -------
    A tuple containing, in order,
    best_individual: The best individual found in all runs
    evals: a list of eval count at that data point
    average_penalized_maxes: local max penalized fitness, averaged over runs
    average_penalized_means: local average penalized fitness, averaged over runs
    average_base_maxes: local max base fitness, averaged over runs
    average_base_means: local average base fitness, averaged over runs
    average_valid_proportion: local proportion of valid solutions, averaged over runs

    '''
    overall_best_individual = LinearGenotype()
    overall_best_individual.base_fitness = -100

    x_evals = None
    total_penalized_maxes = None
    total_penalized_means = None
    total_base_maxes = None
    total_base_means = None
    total_valid_proportions = None

    run_count = len(filenames)

    for name in filenames:
        res = load_data_log(name)
        best_fitness, best_individual, evals, penalized_maxes, penalized_means, base_maxes, base_means, valid_proportion = res
        if best_fitness > overall_best_individual.base_fitness:
            overall_best_individual = best_individual
            overall_best_individual.base_fitness = best_fitness
            
        if x_evals is None:
            x_evals = evals
        if total_penalized_maxes == None:
            total_penalized_maxes = penalized_maxes
        else:
            for i, v in enumerate(penalized_maxes):
                total_penalized_maxes[i] += v

        if total_penalized_means == None:
            total_penalized_means = penalized_means
        else:
            for i, v in enumerate(penalized_means):
                total_penalized_means[i] += v

        if total_base_maxes == None:
            total_base_maxes = base_maxes
        else:
            for i, v in enumerate(base_maxes):
                total_base_maxes[i] += v

        if total_base_means == None:
            total_base_means = base_means
        else:
            for i, v in enumerate(base_means):
                total_base_means[i] += v

        if total_valid_proportions == None:
            total_valid_proportions = valid_proportion
        else:
            for i, v in enumerate(valid_proportion):
                total_valid_proportions[i] += v
        
    average_penalized_maxes = [x/run_count for x in total_penalized_maxes]
    average_penalized_means = [x/run_count for x in total_penalized_means]
    average_base_maxes = [x/run_count for x in total_base_maxes]
    average_base_means = [x/run_count for x in total_base_means]
    average_valid_proportions = [x/run_count for x in total_valid_proportions]
    return overall_best_individual, x_evals, average_penalized_maxes, average_penalized_means, average_base_maxes, average_base_means, average_valid_proportions
