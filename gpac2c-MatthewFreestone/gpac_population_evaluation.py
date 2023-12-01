
# gpac_population_evaluation.py

from fitness import *
from dataclasses import dataclass, field
from tree_genotype import TreeGenotype
from heapq import heappop, heappush

# 2b TODO: Evaluate the population and assign base_fitness, fitness, and log
#          member variables as described in the Assignment 2b notebook.
def base_population_evaluation(population, parsimony_coefficient, experiment, **kwargs):
    if experiment.casefold() == 'green':
        # Evaluate a population of Pac-Man controllers against the default ghost agent.
        # Sample call: score, log = play_GPac(controller, **kwargs)
        pass

    elif experiment.casefold() == 'yellow':
        # YELLOW: Evaluate a population of Pac-Man controllers against the default ghost agent.
        # Use a different parsimony pressure technique than your green experiment.
        # Sample call: score, log = play_GPac(controller, **kwargs)
        pass

    elif experiment.casefold() == 'red1':
        # RED1: Evaluate a population of Pac-Man controllers against the default ghost agent.
        # Apply parsimony pressure as a second objective to be minimized, rather than a penalty.
        # Sample call: score, log = play_GPac(controller, **kwargs)
        pass

    elif experiment.casefold() == 'red2':
        # RED2: Evaluate a population of Pac-Man controllers against the default ghost agent.
        # Sample call: score, log = play_GPac(controller, **kwargs)
        pass

    elif experiment.casefold() == 'red3':
        # RED3: Evaluate a population where each game has multiple different Pac-Man controllers.
        # You must write your own play_GPac_multicontroller function, and use that.
        pass

    elif experiment.casefold() == 'red4':
        # RED4: Evaluate a population of ghost controllers against the default Pac-Man agent.
        # Sample call: score, log = play_GPac(None, controller, **kwargs)
        pass

    elif experiment.casefold() == 'red5':
        # RED5: Evaluate a population where each game has multiple different ghost controllers.
        # You must write your own play_GPac_multicontroller function, and use that.
        pass


def competitive_population_evaluation(pac_population, ghost_population, 
                                      pac_parsimony_coefficient, 
                                      ghost_parsimony_coefficient, sample_size, **kwargs):
    for i in pac_population:
        i.base_fitness = 0
    for i in ghost_population:
        i.base_fitness = 0
    @dataclass(order = True)
    class HeapItem:
        evals: int
        individual: TreeGenotype = field(compare=False)
        def __iter__(self):
            return iter((self.evals, self.individual))
        
    
    pac_heap = [HeapItem(0, i) for i in pac_population]
    ghost_heap = [HeapItem(0, i) for i in ghost_population]
    random.shuffle(pac_heap)
    random.shuffle(ghost_heap)

    # try to drain pacheap first. Then, we'll look at ghosts.
    while pac_heap[0].evals < sample_size:
        pac_evals, pac_ctrl = heappop(pac_heap)
        ghost_evals, ghost_ctrl = heappop(ghost_heap)
        score, _ = play_GPac(pac_ctrl, ghost_ctrl, **kwargs)
        pac_ctrl.base_fitness += score
        ghost_ctrl.base_fitness -= score
        heappush(pac_heap, HeapItem(pac_evals + 1, pac_ctrl))
        heappush(ghost_heap, HeapItem(ghost_evals + 1, ghost_ctrl))

    # look at ghosts.
    while ghost_heap[0].evals < sample_size:
        pac_evals, pac_ctrl = heappop(pac_heap)
        ghost_evals, ghost_ctrl = heappop(ghost_heap)
        score, _ = play_GPac(pac_ctrl, ghost_ctrl, **kwargs)
        pac_ctrl.base_fitness += score
        ghost_ctrl.base_fitness -= score
        heappush(pac_heap, HeapItem(pac_evals + 1, pac_ctrl))
        heappush(ghost_heap, HeapItem(ghost_evals + 1, ghost_ctrl))
    
    for e, i in pac_heap:
        i.base_fitness /= e
        i.fitness = i.base_fitness - len(i.genes)*pac_parsimony_coefficient
    for e, i in ghost_heap:
        i.base_fitness /= e
        i.fitness = i.base_fitness - len(i.genes)*ghost_parsimony_coefficient