from snake_eyes import read_config
from tree_genotype import TreeGenotype
from fitness import play_GPac
from typing import Tuple, List, Callable
import json

def run_and_log(search_fn: Callable[[int, str], Tuple], number_evaluations: int, config_filename:str, result_filename: str):
    best_fitness, best_fitness_progression, best_tree, best_log = search_fn(number_evaluations, config_filename)
    saved_data = {
        'best_fitness': best_fitness,
        'best_fitness_progression': best_fitness_progression,
        'best_tree': best_tree,
        'best_log': best_log
    }
    with open(result_filename, 'w') as f:
        json.dump(saved_data, f, indent=4)


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