from snake_eyes import read_config
from tree_genotype import TreeGenotype
from genetic_programming import GeneticProgrammingPopulation
from fitness import play_GPac
from gpac_population_evaluation import base_population_evaluation
from typing import Tuple, List, Callable, Hashable
import json
import statistics
from selection import *

def red5_run_and_log(search_fn: Callable[[int, str], dict], number_evaluations: int, config_filename:str, result_filename: str):
    res = search_fn(number_evaluations, config_filename)
    with open(result_filename, 'w') as f:
        json.dump(res, f, indent=2)


def red5_genetic_programming_search(number_evaluations, config_filename) -> dict:
    get_penalized_fitness = lambda x: x.fitness
    get_base_fitness = lambda x: x.base_fitness

    def penalized_local_best_and_mean(population: List[TreeGenotype]) -> Tuple[TreeGenotype,float]:
        '''Given a population, returns the penalized fittest solution and the average pop penalized fitness'''
        penalized_fittest_individual = max(population, key = get_penalized_fitness)
        mean_penalized_fitness = statistics.mean(map(get_penalized_fitness, population))
        return penalized_fittest_individual, mean_penalized_fitness

    def base_local_best_and_mean(population: List[TreeGenotype]) -> Tuple[TreeGenotype,float]:
        '''Given a population, returns the base fittest solution and the average pop base fitness'''
        base_fittest_individual = max(population, key = get_base_fitness)
        base_fittest_individual = max(population, key = get_base_fitness)
        mean_base_fitness = statistics.mean(map(get_base_fitness, population))
        return base_fittest_individual, mean_base_fitness

    config = read_config(config_filename, globals(), locals())
    gp = GeneticProgrammingPopulation(**config['ea'], **config)
    evaluations_log = []
    best_penalized_fitness_log = []
    mean_penalized_fitness_log = []
    best_base_fitness_log = []
    mean_base_fitness_log = []

    global_best_score, global_best_genes, global_best_log = \
        base_population_evaluation(gp.population, **config['fitness_kwargs'], **config['game'])

    gp.evaluations = len(gp.population)
    local_penalized_fittest, local_mean_penalized_fitness = penalized_local_best_and_mean(gp.population)
    global_base_fittest, local_mean_base_fitness = base_local_best_and_mean(gp.population)

    evaluations_log.append(gp.evaluations)
    best_penalized_fitness_log.append(local_penalized_fittest.fitness)
    mean_penalized_fitness_log.append(local_mean_penalized_fitness)
    best_base_fitness_log.append(global_base_fittest.base_fitness)
    mean_base_fitness_log.append(local_mean_base_fitness)

    while(gp.evaluations < number_evaluations):
        # SPECIAL FEATURE OF THIS 
        children = gp.generate_children()
        gp.population += children
        #evaluate children
        local_best_score, local_best_genes, local_best_log = \
                base_population_evaluation(gp.population, **config['fitness_kwargs'], **config['game'])
        if local_best_score > global_best_score:
            global_best_score = local_best_score
            global_best_genes = local_best_genes
            global_best_log = local_best_log

        gp.evaluations += len(gp.population)
        # Do selection to determine who survives
        gp.survival()

        #Add values to the log after the initial generation
        local_penalized_fittest, local_mean_penalized_fitness = penalized_local_best_and_mean(gp.population)
        local_base_fittest, local_mean_base_fitness = base_local_best_and_mean(gp.population)

        global_base_fittest = max((global_base_fittest, local_base_fittest), key=get_base_fitness)

        # remove log from all but base fittest
        for i in gp.population:
            if i.base_fitness != local_base_fittest.base_fitness:
                i.log = None

        evaluations_log.append(gp.evaluations)
        best_penalized_fitness_log.append(local_penalized_fittest.fitness)
        mean_penalized_fitness_log.append(local_mean_penalized_fitness)
        best_base_fitness_log.append(local_base_fittest.base_fitness)
        mean_base_fitness_log.append(local_mean_base_fitness)
        
    saved_data = {
        'best_fitness': global_best_score,
        'best_3_genes': global_best_genes,
        'evaluations': evaluations_log,
        'best_penalized_fitness': best_penalized_fitness_log,
        'mean_penalized_fitness': mean_penalized_fitness_log,
        'best_base_fitness': best_base_fitness_log,
        'mean_base_fitness': mean_base_fitness_log,
        'gp_log': gp.log,
        'best_game_log': global_best_log
    }
    return saved_data