
# stock_population_evaluation.py

from cutting_stock.fitness_functions import *
from collections import deque

def base_population_evaluation(population, **kwargs):
    for i in population:
        res = base_fitness_function(i.genes, **kwargs)
        i.fitness, i.visualize = res['fitness'],res['visualize']

# 1c TODO: Evaluate the population and assign the base_fitness, violations, fitness, and visualize
# member variables as described in the constraint satisfaction portion of Assignment 1c
def unconstrained_population_evaluation(population, penalty_coefficient, red=None, **kwargs):
    '''Evaluate the population and assign their fitness members accordingly.
    Return the actual unconstrained fitness with no penalty coefficient
    '''
    unconstrained_fitnesses = []

    if not red:
        for i in population:
            res = unconstrained_fitness_function(i.genes, **kwargs)
            # Assign member variables based on the evaluation
            i.base_fitness = res['base fitness']
            i.violations = res['violations']
            i.fitness = res['unconstrained fitness'] - i.violations * penalty_coefficient
            i.visualize = res['visualize']
            unconstrained_fitnesses.append(res['unconstrained fitness'])
    else:
        for individual in population:
            shapes, bounds = kwargs['shapes'], kwargs['bounds']
            cells = impl.place_all(individual.genes, shapes, bounds)
            violations = impl.count_overlaps(cells) + impl.count_out_of_bounds(cells, bounds)
            # make a deep copy
            if violations:
                # we get a list of all the places there's overlaps, and we try moving shapes in each direction until there isn't
                bad_cells = set()
                bad_shapes = set()
                # print(cells)
                for loc, residents in cells.items():
                    if len(residents) > 1:
                        for r in residents: bad_shapes.add(r)
                    bad_cells.add(loc)
                
                original_cells = []

                # DFS removal of a shape
                def removeShape(curr, shapeid):
                    if curr not in original_cells:
                        original_cells[curr] = cells[curr]

                    cells[curr].remove(shapeid)
                    if len(cells[curr] <= 1):
                        bad_cells.remove()
                    for adj in impl.get_neighbors(curr):
                        removeShape(adj, shapeid)

                # make cells back into what it was
                def restore_original(cells):
                    for loc, value in original_cells:
                        cells[loc] = value
                    original_cells = []

                # items in queue are each [(shape, (dx,dy))]
                queue = deque()
                for shape in bad_shapes:
                    shape_location = individual.genes[shape][:-1]
                    for adj in impl.get_neighbors(shape_location):
                        if impl.in_bounds(adj, bounds):
                            queue.append([shape, adj])
                while bad_cells and queue:
                    all_changes = queue.popleft()
                    new_bad_cells = {}
                    for shape, new_loc in all_changes:
                        shape_location = individual.genes[shape]
                        removeShape(shape_location, shape)
                        new_cells = impl.place_shape(shape, shape_location)

                        # we'll just make locally optimal choices
                        # for adj in impl.get_neighbors(curr_shape_location)


            res = unconstrained_fitness_function(individual.genes, **kwargs)
            # Assign member variables based on the evaluation
            individual.base_fitness = res['base fitness']
            individual.violations = res['violations']
            individual.fitness = res['unconstrained fitness']
            individual.visualize = res['visualize']
            unconstrained_fitnesses.append(res['unconstrained fitness'])

        # RED deliverable logic goes here
    return unconstrained_fitnesses


# 1d TODO: Evaluate the population and assign the objectives and visualize
# member variables as described in the multi-objective portion of Assignment 1d
def multiobjective_population_evaluation(population, yellow=None, red=None, **kwargs):
    # Use multiobjective_fitness_function, i.e.,
    # multiobjective_fitness_function(individual.genes, **kwargs)
    assert not (yellow and red)
    if not (yellow or red):
        # GREEN deliverable logic goes here
        pass

    elif yellow:
        # YELLOW deliverable logic goes here
        pass

    elif red:
        # RED deliverable logic goes here
        pass
