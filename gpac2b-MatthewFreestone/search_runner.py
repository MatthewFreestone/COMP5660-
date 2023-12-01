from snake_eyes import read_config
from tree_genotype import TreeGenotype
from genetic_programming import GeneticProgrammingPopulation
from fitness import play_GPac
from gpac_population_evaluation import base_population_evaluation
from typing import Tuple, List, Callable
import json
import statistics
from selection import *

def run_and_log(search_fn: Callable[[int, str], Tuple], number_evaluations: int, config_filename:str, result_filename: str):
    res = search_fn(number_evaluations, config_filename)
    global_fittest, evaluations, best_penalized_fitness, mean_penalized_fitness, best_base_fitness, mean_base_fitness, gp_log = res
    saved_data = {
        'best_fitness': global_fittest.base_fitness,
        'best_genes': str(global_fittest.genes),
        'evaluations': evaluations,
        'best_penalized_fitness': best_penalized_fitness,
        'mean_penalized_fitness': mean_penalized_fitness,
        'best_base_fitness': best_base_fitness,
        'mean_base_fitness': mean_base_fitness,
        'gp_log': gp_log,
        'best_game_log': global_fittest.log
    }
    with open(result_filename, 'w') as f:
        json.dump(saved_data, f, indent=2)


def genetic_programming_search(number_evaluations, config_filename) -> Tuple[TreeGenotype, List[int], List[float], List[float], List[float], List[float], List[str]]:
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
    global_base_fittest = None

    base_population_evaluation(gp.population, **config['fitness_kwargs'], **config['game'])

    gp.evaluations = len(gp.population)
    local_penalized_fittest, local_mean_penalized_fitness = penalized_local_best_and_mean(gp.population)
    global_base_fittest, local_mean_base_fitness = base_local_best_and_mean(gp.population)

    # remove log from all but base fittest
    for i in gp.population:
        if i.base_fitness != global_base_fittest.base_fitness:
            i.log = None

    evaluations_log.append(gp.evaluations)
    best_penalized_fitness_log.append(local_penalized_fittest.fitness)
    mean_penalized_fitness_log.append(local_mean_penalized_fitness)
    best_base_fitness_log.append(global_base_fittest.base_fitness)
    mean_base_fitness_log.append(local_mean_base_fitness)

    while(gp.evaluations < number_evaluations):
        children = gp.generate_children()
        #evaluate children
        base_population_evaluation(children, **config['fitness_kwargs'], **config['game'])

        gp.evaluations += len(children)
        gp.population += children

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
    
    return global_base_fittest, evaluations_log, best_penalized_fitness_log, mean_penalized_fitness_log, \
                                                                             best_base_fitness_log, mean_base_fitness_log, gp.log

def random_tree_search(number_evaluations, config_filename) -> Tuple[float, List[float], str, List[str]]:
    # Parse the config and implement your random search here.
    # Feel free to focus on implementation first and then return for data collection.
    config = read_config(config_filename, globals(), locals())
    population = TreeGenotype.initialization(number_evaluations, **config['pac_init'])

    best_fitness = -float('inf')
    best_log = None
    best_tree = None
    best_fitness_progression = []

    for i, tree in enumerate(population):
        score, log = play_GPac(tree, **config['game'])
        if score > best_fitness:
            best_fitness = score
            best_log = log
            best_tree = tree
        best_fitness_progression.append((i, best_fitness))
        
    
    # Return whatever data you wish!
    return best_fitness, best_fitness_progression, str(best_tree.genes), best_log

def random_ghost_tree_search(number_evaluations, config_filename) -> Tuple[float, List[float], str, List[str]]:
    config = read_config(config_filename, globals(), locals())
    population = TreeGenotype.initialization(number_evaluations, **config['ghost_init'])

    best_fitness = float('inf')
    best_log = None
    best_tree = None
    best_fitness_progression = []

    for i, tree in enumerate(population):
        # we want low fitness. Our best run is where pacman does bad
        score, log = play_GPac(None, ghost_controller=tree, **config['game'])
        if score < best_fitness:
            best_fitness = score
            best_log = log
            best_tree = tree
        best_fitness_progression.append((i, best_fitness))
        
    
    # Return whatever data you wish!
    return best_fitness, best_fitness_progression, str(best_tree.genes), best_log