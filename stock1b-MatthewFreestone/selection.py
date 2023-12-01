
# selection.py

import random
from itertools import accumulate
# For all the functions here, it's strongly recommended to
# review the documentation for Python's random module:
# https://docs.python.org/3/library/random.html

# Reused functions --------------------------
def get_fitness_weights(population):
    min_fit = min((i.fitness for i in population))
    # if any of their fitnesses are < 0, we should do some scaling
    # if our lowest fitness is -1, we should scale all points by -1
    scale = -1 * min(min_fit, 0)
    scaled_fitnesses = [i.fitness + scale for i in population]
    total_fitnesses = sum(scaled_fitnesses)
    if total_fitnesses == 0:
        # we probably had all negative equal weights and scaled them all to 0. 
        # do uniform random
        return [1] * len(population)
    return [i/total_fitnesses for i in scaled_fitnesses]

# Parent selection functions---------------------------------------------------
def uniform_random_selection(population, n, **kwargs):
    return random.choices(population, k=n)


def k_tournament_with_replacement(population, n, k, **kwargs):
    # the use of a list comprehension here is required, as [...] * n will create a list of n references to the same list
    # random.sample selects k, and the max determines the contest winner
    return [max(random.sample(population, k), key = lambda x: x.fitness) for _ in range(n)]

def fitness_proportionate_selection(population, n, **kwargs):
#     min_fit = min((i.fitness for i in population))
#     # if any of their fitnesses are < 0, we should do some scaling
#     # if our lowest fitness is -1, we should scale all points by -1
#     scale = -1 * min(min_fit, 0)
#     scaled_fitnesses = [i.fitness + scale for i in population]
#     total_fitnesses = sum(scaled_fitnesses)
#     if total_fitnesses == 0:
#         # we probably had all negative equal weights and scaled them all to 0. 
#         # do uniform random
#         return uniform_random_selection(population, n, **kwargs)
#     probabilities = [i/total_fitnesses for i in scaled_fitnesses]
    weighted_pmf = get_fitness_weights(population)
    return random.choices(population, k=n, weights=weighted_pmf)


# Survival selection functions-------------------------------------------------
def truncation(population, n, **kwargs):
    # numpy has an O(n) argpartition, but the builtin sort is probably ok for the size of our populations
    return sorted(population, reverse=True, key=lambda x: x.fitness)[:n]


def k_tournament_without_replacement(population, n, k, **kwargs):
    idx_to_individual = dict(enumerate(population))
    survivors = []
    for _ in range(n):
        contestants_idx = random.sample(list(idx_to_individual.keys()), k)
        # holds the index of the winner in the contestants list
        winner_idx = max(contestants_idx, key=lambda x: idx_to_individual[x].fitness)
        winner = idx_to_individual[winner_idx]
        survivors.append(winner)
        # only remove the winner, since we're doing without replacement
        del idx_to_individual[winner_idx] 
    return survivors



# Yellow deliverable parent selection function---------------------------------
def stochastic_universal_sampling(population, n, sus_distrobution='fitness_proportionate', **kwargs):
    # assuming uniform cdf, maybe will add param later
    assert sus_distrobution in {'uniform', 'fitness_proportionate'}
    if sus_distrobution == 'uniform':
        cdf = list(np.arange(0,1,n))
    else:
        pmf = get_fitness_weights(population)
        # accumulate docs https://docs.python.org/3/library/itertools.html#itertools.accumulate
        # it basically returns running total, converting pmf to a cdf
        cdf_raw = list(accumulate(pmf))
        total = sum(pmf)
        cdf = [i/total for i in cdf_raw]
    results = []
    current_member = 0
    i = 0
    # select number in [0,1], then multiple by 1/n to get [0,1/n]
    r = random.random() * (1/n)
    while (current_member < n):
        while (r <= cdf[i]):
            results.append(population[i])
            r += 1/n
            current_member += 1
        i += 1
    return results

        
        
    
