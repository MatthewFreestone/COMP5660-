
# cutting_stock/fitness_functions.py

import cutting_stock.implementation as impl
import cutting_stock.visualizer as viz
from functools import partial

'''Base fitness function for Assignments 1a and 1b.

Evaluates the input solution on the input problem.

For standard use (not minimize_area), fitness is the total length of stock, minus the used length of stock.
If the solution is invalid (any Shapes overlap or are out-of-bounds), returns failure_fitness.

Returns a dictionary containing the fitness and a function that can be called to obtain a figure.

@param solution: indexable collection of placements, defining shape positions
@param shapes: indexable collection of shapes, of the same length as solution
@param bounds: bounds of the problem
@param failure_fitness: fitness to assign to solutions that violate constraints
@param minimize_area: if True, fitness is calculated using the solution's bounding box area
@return: dict containing values explained above
'''
def base_fitness_function(solution, shapes, bounds, failure_fitness, minimize_area, **kwargs):
    cells = impl.place_all(solution, shapes, bounds)

    if impl.count_overlaps(cells) or impl.count_out_of_bounds(cells, bounds):
        # Violations are not allowed, and all solutions with any violations are equally bad.
        fitness = failure_fitness

    else:
        if not minimize_area:
            # Fitness is the total length minus the used length
            fitness = bounds[0][1] - impl.get_extent(cells, False)
        else:
            # Fitness is the total area minus the used area
            used_area = impl.get_extent(cells, False) * impl.get_extent(cells, True)
            fitness = bounds[0][1] * bounds[1][1] - used_area

    return {
        'fitness': fitness,
        'visualize': partial(viz.get_figure, cells=cells, shapes=shapes, bounds=bounds, **kwargs)
    }


'''Constraint satisfaction fitness function for Assignment 1c.

This is similar to base_fitness_function, except fitness has been renamed to base_fitness,
and there are two new outputs (violations and unconstrained_fitness).

unconstrained_fitness is the fitness a solution would have if we ignore the
two constraints that shapes must be entirely in-bounds and must not overlap.

violations is a count of the number of times the constraints are violated,
i.e., the number of cells that are out-of-bounds and the number of overlapping cells.
It serves as a quantification of how badly a solution violated the constraints.

@param solution: indexable collection of placements, defining shape positions
@param shapes: indexable collection of shapes, of the same length as solution
@param bounds: bounds of the problem
@param failure_fitness: fitness to assign to solutions that violate constraints
@param minimize_area: if True, fitness is calculated using the solution's bounding box area
@return: dict containing values explained above
'''
def unconstrained_fitness_function(solution, shapes, bounds, failure_fitness, minimize_area, **kwargs):
    cells = impl.place_all(solution, shapes, bounds)

    # Unconstrained fitness ignores all violations
    if not minimize_area:
        # Fitness is the total length minus the used length
        unconstrained_fitness = bounds[0][1] - impl.get_extent(cells, False)
    else:
        # Fitness is the total area minus the used area
        used_area = impl.get_extent(cells, False) * impl.get_extent(cells, True)
        unconstrained_fitness = bounds[0][1] * bounds[1][1] - used_area

    # Count all violations
    violations = impl.count_overlaps(cells) + impl.count_out_of_bounds(cells, bounds)

    if violations:
        # All solutions with any violations have equally bad base fitness.
        base_fitness = failure_fitness
    else:
        base_fitness = unconstrained_fitness

    return {
        'base fitness': base_fitness,
        'unconstrained fitness': unconstrained_fitness,
        'violations': violations,
        'visualize': partial(viz.get_figure, cells=cells, shapes=shapes, bounds=bounds, **kwargs)
    }


'''Multiobjective satisfaction fitness function for Assignment 1d.

This function calculates fitness similarly to basic_fitness_function,
but returns two fitness values: one minimizing length, the other minimizing width.
These are x fitness and y fitness respectively.

@param solution: indexable collection of placements, defining shape positions
@param shapes: indexable collection of shapes, of the same length as solution
@param bounds: bounds of the problem
@param failure_fitness: fitness to assign to solutions that violate constraints
@return: dict containing values explained above
'''
def multiobjective_fitness_function(solution, shapes, bounds, failure_fitness, **kwargs):
    cells = impl.place_all(solution, shapes, bounds)

    if impl.count_overlaps(cells) or impl.count_out_of_bounds(cells, bounds):
        # All solutions with any violations are equally bad.
        x_fitness = failure_fitness
        y_fitness = failure_fitness
    else:
        x_fitness = bounds[0][1] - impl.get_extent(cells, False)
        y_fitness = bounds[1][1] - impl.get_extent(cells, True)

    return {
        'x fitness': x_fitness,
        'y fitness': y_fitness,
        'visualize': partial(viz.get_figure, cells=cells, shapes=shapes, bounds=bounds, **kwargs)
    }

