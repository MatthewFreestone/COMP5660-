
# stock_population_evaluation.py

from cutting_stock.fitness_functions import *

# 1b TODO: Evaluate the population and assign the fitness and visualize
# member variables as described in the Assignment 1b notebook
def base_population_evaluation(population, **kwargs):
    for i in population:
        res = base_fitness_function(i.genes, **kwargs)
        i.fitness, i.visualize = res['fitness'],res['visualize']
    # Use base_fitness_function, i.e.,
    # base_fitness_function(individual.genes, **kwargs)


# 1c TODO: Evaluate the population and assign the fitness, base_fitness, and visualize
# member variables as described in the constraint satisfaction portion of Assignment 1c
def unonstrained_population_evaluation(population, penalty_coefficient, yellow=None, **kwargs):
    # Use unconstrained_fitness_function
    if not yellow:
        # GREEN deliverable logic goes here
        pass

    else:
        # YELLOW deliverable logic goes here
        pass


# 1c TODO: Evaluate the population and assign the objectives and visualize
# member variables as described in the multi-objective portion of Assignment 1c
def multi_objective_population_evaluation(population, yellow=None, red=None, **kwargs):
    assert not (yellow and red)
    # Use multiobjective_fitness_function
    if not (yellow or red):
        # GREEN deliverable logic goes here
        pass

    if yellow:
        # YELLOW deliverable logic goes here
        pass

    if red:
        # RED deliverable logic goes here
        pass
