from typing import Tuple, List
import statistics
from collections import deque
from snake_eyes import read_config
from linear_genotype import LinearGenotype
from base_evolution import BaseEvolutionPopulation
from stock_population_evaluation import unconstrained_population_evaluation
from log_analyzer import analyze_constraint_satisfaction_log
from selection import *
from math import sqrt

get_penalized_fitness = lambda x: x.fitness
get_base_fitness = lambda x: x.base_fitness
def penalized_local_best_and_mean(population: List[LinearGenotype]) -> Tuple[LinearGenotype,float]:
    '''Given a population, returns the penalized fittest solution and the average pop penalized fitness'''
    penalized_fittest_individual = max(population, key = get_penalized_fitness)
    mean_penalized_fitness = statistics.mean(map(get_penalized_fitness, population))
    return penalized_fittest_individual, mean_penalized_fitness

def base_local_best_and_mean(population: List[LinearGenotype]) -> Tuple[LinearGenotype,float]:
    '''Given a population, returns the base fittest solution and the average pop base fitness'''
    base_fittest_individual = max(population, key = get_base_fitness)
    base_fittest_individual = max(population, key = get_base_fitness)
    mean_base_fitness = statistics.mean(map(get_base_fitness, population))
    return base_fittest_individual, mean_base_fitness

def update_penalty_coef(config, prev_std, curr_uncon_fitnesses, adaptive_penalty_coef):
    curr_std = sqrt(statistics.variance(curr_uncon_fitnesses)) * adaptive_penalty_coef
    # intutition: if the variance is high, we have lots of genetic variety, and we should encorage the created 
    # ones to be valid. When it is low, we are ok with prioritizing exploring invalid
    prev_std.append(curr_std)
    next_coef = statistics.mean(prev_std)
    next_coef = min(next_coef, 2)
    config['problem']['penalty_coefficient'] = next_coef


def constraint_satisfaction_EA_search(number_evaluations, config_filename):
    global_base_fittest = None
    config = read_config(config_filename, globals(), locals())
    use_adaptive_penalty_coef = config['ea'].get('yellow', False) 
    adaptive_penalty_coef = config['ea'].get('adaptive_penalty_coefficient', None)
    base_ea = BaseEvolutionPopulation(**config['ea'], **config)
    data_log = []
    prev_stds = deque(maxlen=5)


    curr_uncon_fitness = unconstrained_population_evaluation(base_ea.population, **config['problem'])
    if use_adaptive_penalty_coef:
        update_penalty_coef(config, prev_stds, curr_uncon_fitness, adaptive_penalty_coef)
    base_ea.evaluations = len(base_ea.population)
        
    #Add values to the log after the initial generation
    base_ea.log.append(f'Evaluations: {base_ea.evaluations}')

    local_penalized_fittest, local_mean_penalized_fitness = penalized_local_best_and_mean(base_ea.population)
    base_ea.log.append(f'Local best penalized fitness: {local_penalized_fittest.fitness}')
    base_ea.log.append(f'Local mean penalized fitness: {local_mean_penalized_fitness}')

    # on the first round, we can assign global_fittest to be some arbitrary individual on base fitness
    global_base_fittest, local_mean_base_fitness = base_local_best_and_mean(base_ea.population)
    base_ea.log.append(f'Local best base fitness: {global_base_fittest.base_fitness}')
    base_ea.log.append(f'Local mean base fitness: {local_mean_base_fitness}')
    
    valid_soln_count = [x.violations for x in base_ea.population].count(0)
    base_ea.log.append(f'Number of valid solutions: {valid_soln_count}')
    data_log.append(f"{base_ea.evaluations} {local_penalized_fittest.fitness} \
                    {local_mean_penalized_fitness} {global_base_fittest.base_fitness} {local_mean_base_fitness} {valid_soln_count/base_ea.mu}")

    
    ### Start Children Section ###
    while(base_ea.evaluations < number_evaluations):
        children = base_ea.generate_children()

        #evaluate children
        curr_uncon_fitness = unconstrained_population_evaluation(children, **config['problem'])
        if use_adaptive_penalty_coef:
            update_penalty_coef(config, prev_stds, curr_uncon_fitness, adaptive_penalty_coef)
        base_ea.evaluations += len(children)
        base_ea.population += children

        # Do selection to determine who survives
        base_ea.survival()

        #Add values to the log after the initial generation
        base_ea.log.append(f'Evaluations: {base_ea.evaluations}')
        local_penalized_fittest, local_mean_penalized_fitness = penalized_local_best_and_mean(base_ea.population)
        base_ea.log.append(f'Local best penalized fitness: {local_penalized_fittest.fitness}')
        base_ea.log.append(f'Local mean penalized fitness: {local_mean_penalized_fitness}')


        local_base_fittest, local_mean_base_fitness = base_local_best_and_mean(base_ea.population)
        base_ea.log.append(f'Local best base fitness: {local_base_fittest.base_fitness}')
        base_ea.log.append(f'Local mean base fitness: {local_mean_base_fitness}')

        global_base_fittest = max((global_base_fittest, local_base_fittest), key=get_base_fitness)

        valid_soln_count = [x.violations for x in base_ea.population].count(0)

        base_ea.log.append(f'Number of valid solutions: {valid_soln_count}')
        data_log.append(f"{base_ea.evaluations} {local_penalized_fittest.fitness} {local_mean_penalized_fitness} \
                        {local_base_fittest.base_fitness} {local_mean_base_fitness} {valid_soln_count/base_ea.mu}")
    
    # This will print outputs if it looks like anything has gone wrong.
    analyze_constraint_satisfaction_log(base_ea.log, number_evaluations)

    return base_ea.log, data_log, global_base_fittest