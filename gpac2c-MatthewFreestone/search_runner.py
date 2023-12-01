from snake_eyes import read_config
from tree_genotype import TreeGenotype
from genetic_programming import GeneticProgrammingPopulation
from fitness import play_GPac
from gpac_population_evaluation import competitive_population_evaluation
from typing import Tuple, List, Callable
import json
import statistics
from selection import *

def run_and_log(search_fn: Callable[[int, str], Tuple], number_evaluations: int, config_filename:str, result_filename: str):
    res = search_fn(number_evaluations, config_filename)
    with open(result_filename, 'w') as f:
        json.dump(res, f, indent=2)


def competitive_genetic_programming_search(number_evaluations, config_filename) -> Tuple[TreeGenotype, List[int], List[float], List[float], List[float], List[float], List[str]]:
    get_base_fitness = lambda x: x.base_fitness
    def base_local_max_pac_and_ghost(pac_population: List[TreeGenotype], ghost_population: List[TreeGenotype]) -> Tuple[TreeGenotype,TreeGenotype]:
        '''Given a population, returns the base fittest solution and the average pop base fitness'''
        base_fittest_pac = max(pac_population, key = get_base_fitness)
        base_fittest_ghost = max(ghost_population, key = get_base_fitness)
        return base_fittest_pac, base_fittest_ghost

    config = read_config(config_filename, globals(), locals())
    pac_config, ghost_config = split_config(config)

    pac_gp = GeneticProgrammingPopulation(**pac_config['ea'], **pac_config)
    ghost_gp = GeneticProgrammingPopulation(**ghost_config['ea'], **ghost_config)

    competitive_population_evaluation(pac_gp.population, ghost_gp.population, **config['fitness_kwargs'], **config['game'])
    local_fittest_pac, local_fittest_ghost = base_local_max_pac_and_ghost(pac_gp.population, ghost_gp.population)

    evals = max(len(pac_gp.population), len(ghost_gp.population))
    pac_gp.evaluations = evals
    ghost_gp.evaluations = evals

    while(pac_gp.evaluations < number_evaluations):
        pac_children = pac_gp.generate_children()
        ghost_children = ghost_gp.generate_children()
        #evaluate everything again 
        pac_gp.population += pac_children
        ghost_gp.population += ghost_children
        competitive_population_evaluation(pac_gp.population, ghost_gp.population, **config['fitness_kwargs'], **config['game'])
        local_fittest_pac, local_fittest_ghost = base_local_max_pac_and_ghost(pac_gp.population, ghost_gp.population)

        evals = max(len(pac_gp.population), len(ghost_gp.population))
        pac_gp.evaluations += evals
        ghost_gp.evaluations += evals

        # Do selection to determine who survives
        pac_gp.survival()
        ghost_gp.survival()
    
    return {
        'pac_fitness': local_fittest_pac.base_fitness,
        'ghost_fitness': local_fittest_ghost.base_fitness,
        'fittest_pac': str(local_fittest_pac.genes),
        'fittest_ghost': str(local_fittest_ghost.genes),
        'pac_log': pac_gp.log,
        'ghost_log': ghost_gp.log
    }

def split_config(config):
    pac_config = dict()
    ghost_config = dict()

    for key in config:
        if key.startswith('pac_'):
            pac_config[key.partition('_')[-1]] = config[key]

        elif key.startswith('ghost_'):
            ghost_config[key.partition('_')[-1]] = config[key]

        else:
            pac_config[key] = config[key]
            ghost_config[key] = config[key]

    return pac_config, ghost_config
