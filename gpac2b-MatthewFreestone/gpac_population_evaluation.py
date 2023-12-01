
# gpac_population_evaluation.py

from fitness import *
from heapq import heappop, heappush
from dataclasses import dataclass, field
from tree_genotype import TreeGenotype

# 2b TODO: Evaluate the population and assign base_fitness, fitness, and log
#          member variables as described in the Assignment 2b notebook.
def base_population_evaluation(population, parsimony_coefficient, experiment, **kwargs):
    if experiment.casefold() == 'green':
        for i in population:
            score, log = play_GPac(pac_controller=i,**kwargs)
            i.fitness = score - len(i.genes)*parsimony_coefficient
            i.base_fitness = score
            i.log = log
        # Evaluate a population of Pac-Man controllers against the default ghost agent.
        # Sample call: score, log = play_GPac(controller, **kwargs)
        pass

    elif experiment.casefold() == 'yellow':
        for i in population:
            score, log = play_GPac(pac_controller=i,**kwargs)
            i.fitness = score - i.genes.maxDepth() *parsimony_coefficient
            i.base_fitness = score
            i.log = log
        pass

    elif experiment.casefold() == 'red1':
        # RED1: Evaluate a population of Pac-Man controllers against the default ghost agent.
        # Apply parsimony pressure as a second objective to be minimized, rather than a penalty.
        # Sample call: score, log = play_GPac(controller, **kwargs)
        pass

    elif experiment.casefold() == 'red2':
        # RED2: Evaluate a population of Pac-Man controllers against the default ghost agent.
        # Sample call: score, log = play_GPac(controller, **kwargs)
        for i in population:
            # purely a config change!
            score, log = play_GPac(pac_controller=i,**kwargs)
            i.fitness = score - len(i.genes) * parsimony_coefficient
            i.base_fitness = score
            i.log = log

    elif experiment.casefold() == 'red3':
        # RED3: Evaluate a population where each game has multiple different Pac-Man controllers.
        # You must write your own play_GPac_multicontroller function, and use that.
        for i in population:
            i.base_fitness = 0
        # we intentionally want a shallow copy
        # minheap
        @dataclass(order = True)
        class HeapItem:
            evals: int
            individual: TreeGenotype = field(compare=False)
            def __iter__(self):
                return iter((self.evals, self.individual))

        trials = [HeapItem(0, i) for i in population]
        random.shuffle(trials)
        
        best_score = -float('inf')
        best_3_genes = ''
        best_log = ['']

        while trials:
            evals1, first = heappop(trials)
            evals2, second = heappop(trials)
            evals3, third = heappop(trials)
            score, log = play_GPac_multicontroller(pac_controllers=(first, second, third), **kwargs)
            first.base_fitness += score
            second.base_fitness += score
            third.base_fitness += score
            if score > best_score:
                best_score = score
                best_3_genes = [*map(str, (first.genes, second.genes, third.genes))]
                best_log = log

            heappush(trials, HeapItem(evals1 + 1, first))
            heappush(trials, HeapItem(evals2 + 1, second))
            heappush(trials, HeapItem(evals3 + 1, third))
            if evals1 > 3 or evals2 > 3 or evals3 > 3:
                break
        # in the heap, we now have [e, individual] where e is how many times it was evaulated
        # to get average, divide by that number
        for e, i in trials:
            i.base_fitness /= e
            i.fitness = i.base_fitness - len(i.genes)*parsimony_coefficient
            
        return best_score, best_3_genes, best_log

    elif experiment.casefold() == 'red4':
        # RED4: Evaluate a population of ghost controllers against the default Pac-Man agent.
        for i in population:
            # purely a config change!
            score, log = play_GPac(pac_controller=None, ghost_controller=i,**kwargs)
            # becuase we want to minimize score, use negative
            i.fitness = - (score + len(i.genes) * parsimony_coefficient)
            i.base_fitness = -score
            i.log = log
        pass

    elif experiment.casefold() == 'red5':
        for i in population:
            i.base_fitness = 0
        # we intentionally want a shallow copy
        # minheap
        @dataclass(order = True)
        class HeapItem:
            evals: int
            individual: TreeGenotype = field(compare=False)
            def __iter__(self):
                return iter((self.evals, self.individual))

        trials = [HeapItem(0, i) for i in population]
        random.shuffle(trials)
        
        best_score = float('inf')
        best_3_genes = ''
        best_log = ['']

        while trials:
            evals1, first = heappop(trials)
            evals2, second = heappop(trials)
            evals3, third = heappop(trials)
            score, log = play_GPac_multicontroller(pac_controllers=None, ghost_controllers=(first, second, third), **kwargs)
            first.base_fitness -= score
            second.base_fitness -= score
            third.base_fitness -= score
            if score < best_score:
                best_score = score
                best_3_genes = [*map(str, (first.genes, second.genes, third.genes))]
                best_log = log

            heappush(trials, HeapItem(evals1 + 1, first))
            heappush(trials, HeapItem(evals2 + 1, second))
            heappush(trials, HeapItem(evals3 + 1, third))
            if evals1 > 3 or evals2 > 3 or evals3 > 3:
                break
        # in the heap, we now have [e, individual] where e is how many times it was evaulated
        # to get average, divide by that number
        for e, i in trials:
            i.base_fitness /= e
            i.fitness = i.base_fitness - len(i.genes)*parsimony_coefficient
        # since score is negation of fitness, we'll return negative so we can reuse code
        return -best_score, best_3_genes, best_log
