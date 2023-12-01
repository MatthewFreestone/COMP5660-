from typing import Tuple, List
import statistics
from snake_eyes import read_config
from linear_genotype import LinearGenotype
from base_evolution import BaseEvolutionPopulation
from stock_population_evaluation import multiobjective_population_evaluation
from log_analyzer import analyze_multiobjective_log
from multiobjective import assign_fitnesses, calculate_hypervolume
from selection import *

get_length = lambda x: x.objectives[0]
get_width = lambda x: x.objectives[1]
def local_best_and_mean_len_width(population: List[LinearGenotype]) -> Tuple[int, float, int, float]:
    '''Given a population, returns (best length, mean length, best width, mean width)'''
    best_length_individual = max(population, key = get_length)
    best_length = get_length(best_length_individual)
    mean_length = statistics.mean(map(get_length, population))

    best_width_individual = max(population, key=get_width)
    best_width = get_width(best_width_individual)
    mean_width = statistics.mean(map(get_width, population))

    return best_length, mean_length, best_width, mean_width

get_edges = lambda x: x.objectives[2]
def local_best_and_mean_edges(population: List[LinearGenotype]) -> Tuple[float, float]:
    '''Given a population, returns (best edges, mean edges)'''
    best_edges_individual = max(population, key = get_edges)
    best_edges = get_edges(best_edges_individual)
    mean_edges = statistics.mean(map(get_edges, population))

    return best_edges, mean_edges


def multiobjective_EA_search(number_evaluations, config_filename):
    config = read_config(config_filename, globals(), locals())
    yellow = config['problem'].get("yellow", False)
    # if yellow: print("Doing yellow")
    base_ea = BaseEvolutionPopulation(**config['ea'], **config)
    data_log = []

    multiobjective_population_evaluation(base_ea.population, **config['problem'])
    base_ea.evaluations = len(base_ea.population)
        
    # Sort population and assign representative fitnesses
    assign_fitnesses(base_ea.population, **config['problem'])

    #Add values to the log after the initial generation
    best_length, mean_length, best_width, mean_width = local_best_and_mean_len_width(base_ea.population)
    base_ea.log.append(f'Evaluations: {base_ea.evaluations}')
    base_ea.log.append(f'Local best length: {best_length}')
    base_ea.log.append(f'Local mean length: {mean_length}')
    base_ea.log.append(f'Local best width: {best_width}')
    base_ea.log.append(f'Local mean width: {mean_width}')
    pareto_front = [individual for individual in base_ea.population if individual.level == 1]
    hypervolume = calculate_hypervolume(pareto_front)
    base_ea.log.append(f'Individuals in the Pareto front: {len(pareto_front)}')
    base_ea.log.append(f'Local Pareto front mean length: {statistics.mean(map(lambda x:x.objectives[0], pareto_front))}')
    base_ea.log.append(f'Local Pareto front mean width: {statistics.mean(map(lambda x:x.objectives[1], pareto_front))}')
    base_ea.log.append(f'Local Pareto front hypervolume: {hypervolume}')

    if not yellow:
        gen_data = f"{base_ea.evaluations} {best_length} {mean_length} {best_width} {mean_width} {hypervolume}"
    else:
        best_edges, mean_edges = local_best_and_mean_edges(base_ea.population)
        gen_data = f"{base_ea.evaluations} {best_length} {mean_length} {best_width} {mean_width} {best_edges} {mean_edges} {hypervolume}"

    data_log.append(gen_data)
    
    ### Start Children Section ###
    while(base_ea.evaluations < number_evaluations):
        children = base_ea.generate_children()

        #evaluate children
        multiobjective_population_evaluation(children, **config['problem'])
 
        base_ea.evaluations += len(children)
        base_ea.population += children

        assign_fitnesses(base_ea.population, **config['problem'])

        # Do selection to determine who survives
        base_ea.survival()
        assign_fitnesses(base_ea.population, **config['problem'])

        #Add values to the log after the initial generation
        best_length, mean_length, best_width, mean_width = local_best_and_mean_len_width(base_ea.population)
        base_ea.log.append(f'Evaluations: {base_ea.evaluations}')
        base_ea.log.append(f'Local best length: {best_length}')
        base_ea.log.append(f'Local mean length: {mean_length}')
        base_ea.log.append(f'Local best width: {best_width}')
        base_ea.log.append(f'Local mean width: {mean_width}')
        pareto_front = [individual for individual in base_ea.population if individual.level == 1]
        hypervolume = calculate_hypervolume(pareto_front)
        base_ea.log.append(f'Individuals in the Pareto front: {len(pareto_front)}')
        base_ea.log.append(f'Local Pareto front mean length: {statistics.mean(map(lambda x:x.objectives[0], pareto_front))}')
        base_ea.log.append(f'Local Pareto front mean width: {statistics.mean(map(lambda x:x.objectives[1], pareto_front))}')
        base_ea.log.append(f'Local Pareto front hypervolume: {hypervolume}')
        
        if not yellow:
            gen_data = f"{base_ea.evaluations} {best_length} {mean_length} {best_width} {mean_width} {hypervolume}"
        else:
            best_edges, mean_edges = local_best_and_mean_edges(base_ea.population)
            gen_data = f"{base_ea.evaluations} {best_length} {mean_length} {best_width} {mean_width} {best_edges} {mean_edges} {hypervolume}"

        data_log.append(gen_data)
    
    # save the front, as we'll need it
    pareto_front_genes = [individual.genes for individual in base_ea.population if individual.level == 1]

    # This will print outputs if it looks like anything has gone wrong.
    analyze_multiobjective_log(base_ea.log, number_evaluations)

    return base_ea.log, data_log, hypervolume, pareto_front_genes