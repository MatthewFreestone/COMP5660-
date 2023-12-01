import statistics
from snake_eyes import read_config
from linear_genotype import LinearGenotype
from base_evolution import BaseEvolutionPopulation
from stock_population_evaluation import multiobjective_population_evaluation
from multiobjective import calculate_hypervolume, update_pareto_front
from selection import *


def multiobjective_EA_search_red(number_evaluations, config_filename):
    config = read_config(config_filename, globals(), locals())
    base_ea = BaseEvolutionPopulation(**config['ea'], **config)
    multiobjective_population_evaluation(base_ea.population, **config['problem'])
        
    # Sort population and assign representative fitnesses
    base_ea.population = update_pareto_front([], base_ea.population)
    pareto_front = base_ea.population
    # print(pareto_front)

    #Add values to the log after the initial generation
    hypervolume = calculate_hypervolume(pareto_front)
    base_ea.log.append(f'Individuals in the Pareto front: {len(pareto_front)}')
    base_ea.log.append(f'Local Pareto front mean length: {statistics.mean(map(lambda x:x.objectives[0], pareto_front))}')
    base_ea.log.append(f'Local Pareto front mean width: {statistics.mean(map(lambda x:x.objectives[1], pareto_front))}')
    base_ea.log.append(f'Local Pareto front hypervolume: {hypervolume}')
    
    ### Start Generating Random###
    while(base_ea.evaluations < number_evaluations):
        children = LinearGenotype.initialization(base_ea.mu, **config['problem'])

        #evaluate children
        multiobjective_population_evaluation(children, **config['problem'])
 
        base_ea.evaluations += len(children)

        base_ea.population = update_pareto_front(base_ea.population, children)
        pareto_front = base_ea.population

        hypervolume = calculate_hypervolume(pareto_front)
        base_ea.log.append(f'Individuals in the Pareto front: {len(pareto_front)}')
        base_ea.log.append(f'Local Pareto front mean length: {statistics.mean(map(lambda x:x.objectives[0], pareto_front))}')
        base_ea.log.append(f'Local Pareto front mean width: {statistics.mean(map(lambda x:x.objectives[1], pareto_front))}')
        base_ea.log.append(f'Local Pareto front hypervolume: {hypervolume}')
        
    # This will print outputs if it looks like anything has gone wrong.

    return base_ea.log,  hypervolume, [p.genes for p in pareto_front]