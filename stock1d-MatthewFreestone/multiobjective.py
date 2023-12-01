import math
from collections import defaultdict
from itertools import count
from functools import lru_cache


'''
1d TODO: Return True if A dominates B based on the objective member variables of both objects.
If attempting the YELLOW deliverable, your code must be able to gracefully handle
any number of objectives, i.e., don't hardcode an assumption that there are 2 objectives.
'''
def dominates(A, B):
    # re-written at office hours to remove branching. Original function below.
    return (not any(a < b for a, b in zip(A.objectives,B.objectives))) \
        and any(a > b for a, b in zip(A.objectives,B.objectives))
#
# def dominates(A, B):
#     # first, check any of A is lower than B
#     a_lower = (a < b for a, b in zip(A.objectives,B.objectives))
#     if any(a_lower): return False

#     # all of A not lower than B. Check if any is greater
#     a_higher = (a > b for a, b in zip(A.objectives,B.objectives))
#     if any(a_higher): return True

#     # a and b were equal.
#     return False

'''
1d TODO: Use the dominates function (above) to sort the input population into levels
of non-domination, and assign to the level members based on an individual's level.
'''
def nondomination_sort(population):
    # implementation based on https://ieeexplore.ieee.org/abstract/document/996017 
    domination_counters = [0] * len(population)
    # key dominates all values
    dominated_by = defaultdict(set)
    fronts = [set() for _ in range(len(population) + 1)]
    for i, p in enumerate(population):
        for j, q in enumerate(population):
            if dominates(p,q):
                dominated_by[i].add(j)
            elif dominates(q,p):
                domination_counters[i] += 1
        if domination_counters[i] == 0:
            # p belongs to first front
            population[i].level = 1
            fronts[1].add(i)
            
    curr_front = 1
    while len(fronts[curr_front]) > 0:
        next_front = set()
        for i in fronts[curr_front]:
            for j in dominated_by[i]:
                domination_counters[j] -= 1
                if domination_counters[j] == 0:
                    population[j].level = curr_front + 1
                    next_front.add(j)
        curr_front += 1
        fronts[curr_front] = next_front



'''
1d TODO: Calculate the improved crowding distance from https://ieeexplore.ieee.org/document/996017
For each individual in the population, and assign this value to the crowding member variable.
Use the inf constant (imported at the top of this file) to represent infinity where appropriate.
'''
def assign_crowding_distances(population):
    for lvl in {i.level for i in population}:
        # because we're getting objects `i`, it should be pass by reference
        curr_level = [i for i in population if i.level == lvl]
        if not curr_level:
            return
        #initially, set all crowding scores to 0
        for i in curr_level:
            i.crowding = 0
        # this now corresponds to the index of an individual in the population
        for obj_idx in range(len(curr_level[0].objectives)):
            curr_level.sort(key=lambda x: x.objectives[obj_idx])
            curr_level[0].crowding = math.inf
            curr_level[-1].crowding = math.inf
            # shortcut to get the desired objective performance for individual i
            I_i = lambda i: curr_level[i].objectives[obj_idx]
            fmin = I_i(0)
            fmax = I_i(len(curr_level)-1)
            for i in range(1, len(curr_level)-1):
                if (fmax - fmin) != 0:
                    res = (I_i(i+1) - I_i(i-1))/(fmax - fmin)
                    curr_level[i].crowding += res
                else:
                    # division by 0
                    curr_level[i].crowding = math.inf



# This function is implemented for you. You should not modify it.
# It uses the above functions to assign fitnesses to the population.
def assign_fitnesses(population, crowding=False, **kwargs):
    # Assign levels of nondomination.
    nondomination_sort(population)

    # Assign fitnesses.
    max_level = max(map(lambda x:x.level, population))
    for individual in population:
        individual.fitness = max_level + 1 - individual.level

    # Check if we should apply crowding penalties.
    if not crowding:
        for individual in population:
            individual.crowding = 0

    # Apply crowding penalties.
    else:
        assign_crowding_distances(population)
        for individual in population:
            if individual.crowding != math.inf:
                assert 0 <= individual.crowding <= len(individual.objectives),\
                    f'A crowding distance ({individual.crowding}) was not in the correct range. ' +\
                    'Make sure you are calculating them correctly in assign_crowding_distances.'
                individual.fitness -= 1 - 0.999 * (individual.crowding / len(individual.objectives))

def update_pareto_front(existing_front, new_individuals):
    '''The function takes an existing front and some new individuals, the returns the new front
    This should be significantly faster than doing a full sort
    With e = len(existing_front) and n = len(new_individuals)
    Best case: All new individuals are dominated by something on the front. O(ne)
    Worst case: All new individuals belong on the front and do not dominate anything already on the front: O(n*(e+n)) (I think)
    Given that the worst case is very unlikely if there is at least 1 valid solution, this should be signficantly faster
    than a full sort
    '''
    assert len(new_individuals) != 0
    new_pareto_front = set(existing_front) or set()
    for new_i in new_individuals: #O(n)
        # create a list of items already 
        dominates_new = {o for o in new_pareto_front if dominates(o, new_i)} #O(e)
        if len(dominates_new) == 0:
            # find the set difference to get items that might be dominated by new
            might_be_dominated_by_new = new_pareto_front - dominates_new
            for possible_remove in might_be_dominated_by_new:  #O(e+n)
                if dominates(new_i, possible_remove):
                    new_pareto_front.remove(possible_remove)
            new_pareto_front.add(new_i)
        # else, someone does dominated new. we shouldn't add it
    return list(new_pareto_front)

'''
The remainder of this file is code used to calculate hypervolumes.
You do not need to read, modify or understand anything below this point.
Implementation based on https://ieeexplore.ieee.org/document/5766730
'''
def calculate_hypervolume(front, reference_point=None):
    point_set = [individual.objectives for individual in front]
    if reference_point is None:
        # Defaults to (-1)^n, which assumes the minimal possible scores are 0.
        reference_point = [-1] * len(point_set[0])
    return wfg_hypervolume(list(point_set), reference_point, True)


def wfg_hypervolume(pl, reference_point, preprocess=False):
    if preprocess:
        pl_set = {tuple(p) for p in pl}
        pl = list(pl_set)
        if len(pl[0]) >= 4:
            pl.sort(key=lambda x: x[0])

    if len(pl) == 0:
        return 0
    return sum([wfg_exclusive_hypervolume(pl, k, reference_point) for k in range(len(pl))])


def wfg_exclusive_hypervolume(pl, k, reference_point):
    return wfg_inclusive_hypervolume(pl[k], reference_point) - wfg_hypervolume(limit_set(pl, k), reference_point)


def wfg_inclusive_hypervolume(p, reference_point):
    return math.prod([abs(p[j] - reference_point[j]) for j in range(len(p))])


def limit_set(pl, k):
    ql = []
    for i in range(1, len(pl) - k):
        ql.append([min(pl[k][j], pl[k+i][j]) for j in range(len(pl[0]))])
    result = set()
    for i in range(len(ql)):
        interior = False
        for j in range(len(ql)):
            if i != j:
                if all(ql[j][d] >= ql[i][d] for d in range(len(ql[i]))) and any(ql[j][d] > ql[i][d] for d in range(len(ql[i]))):
                    interior = True
                    break
        if not interior:
            result.add(tuple(ql[i]))
    return list(result)

