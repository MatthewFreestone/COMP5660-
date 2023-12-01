
# linear_genotype.py

import random
import numpy as np
from copy import deepcopy

class LinearGenotype():
    def __init__(self):
        self.fitness = None
        self.genes = None

    def random_initialization(self, shapes, bounds, **kwargs):
        result = []
        for _ in range(len(shapes)):
            x = random.randint(bounds[0][0], bounds[0][1] - 1)
            y = random.randint(bounds[1][0], bounds[1][1] - 1)
            r = random.choice([0, 1, 2, 3])
            result.append((x, y, r))
        self.genes = result

    def recombine(self, mate, method, alhpa=0.5, points=2, **kwargs):
        child = LinearGenotype()
        num_genes = len(self.genes)

        # TODO: Recombine genes of self with mate and assign to child's genes member variable
        assert method.casefold() in {'uniform', 'one-point', 'bonus'}
        if method.casefold() == 'uniform':
            picks = (random.choice([0,1]) for _ in range(num_genes))
            child.genes = [self.genes[i] if v == 0 else mate.genes[i] for i,v in enumerate(picks)]

        elif method.casefold() == 'one-point':
            # we only want points that take at least one gene from each parent
            # unlike most python ranges, this is inclusive on both ends
            point = random.randint(1, num_genes-1)

            # taking shallow copies _should_ be ok, since each allele is a tuple, which are immutable values types
            child.genes = self.genes[:point] + mate.genes[point:]

        elif method.casefold() == 'bonus':
            # just like one-point crossover, we can do many-point
            # select points points without replacement, then sort to increasing order
            points = sorted(random.sample(list(range(1, num_genes)), k=points))
            # add the list length to end to get final stretch
            points.append(num_genes)
            parents = [self.genes, mate.genes]
            current_parent = 0 if random.random() < 0.5 else 1
            # take the first part from randomly chosen parent
            res = parents[current_parent][:points[0]]
            # switch to other parent
            current_parent = (current_parent + 1) % 2
            for i in range(len(points)-1):
                stretch = parents[current_parent][points[i]:points[i+1]]
                res += stretch
                current_parent = (current_parent + 1) % 2
            child.genes = res
            assert len(child.genes) == len(self.genes)
        
        return child


    def mutate(self, bounds, bonus=None, normal_std = 1, expected_location_changes = 2, **kwargs):
        '''
        mutate this individual and return the mutated version
        normal_std is used for creep
        expected_location_changes indicates how many places will be touched on this individual
        '''
        mutant = LinearGenotype()
        mutant.genes = deepcopy(self.genes)

        if not bonus:
            x_min, x_max = bounds[0][0], bounds[0][1] - 1
            y_min, y_max = bounds[1][0], bounds[1][1] - 1
            assert expected_location_changes < len(self.genes)
            change_boundary = expected_location_changes / len(self.genes)
            new_genes = []
            for curr in mutant.genes:
                if random.random() > change_boundary:
                    new_genes.append(curr)
                    continue
                x, y, r = curr
                # 25% chance of no change
                r = random.choice([0, 1, 2, 3])

                x_tweak, y_tweak = np.random.normal(loc=0, scale=normal_std, size=2)
                x = int(x + x_tweak)
                # guarantees that x_min <= x <= x_max
                x = max(x_min, min(x, x_max))
                y = int(y + y_tweak)
                # guarantees that y_min <= y <= y_max
                y = max(y_min, min(y, y_max))
                new_genes.append((x,y,r))
            mutant.genes = new_genes

        else:
            '''
            This is a red deliverable (i.e., bonus for anyone).

            Implement the bonus crossover operator as described in deliverable
            Red 1 of Assignment 1b.
            '''
            pass

        return mutant
    
    def __str__(self):
        '''Magic method for printing, makes for better debugging'''
        return f"LinearGenotype({self.fitness=}, {self.genes=})"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def initialization(cls, mu, *args, **kwargs):
        population = [cls() for _ in range(mu)]
        for i in range(len(population)):
            population[i].random_initialization(*args, **kwargs)
        return population
