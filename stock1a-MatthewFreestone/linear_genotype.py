import random
from collections import namedtuple

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
        # TODO: Initialize self.genes, using the input parameters.
        #       It should be an indexable data structure of length len(shapes),
        #       where each element is an indexable data structure of length 3.
        #       The first value of each element should be an integer within the
        #       half-open interval [bounds[0][0], bounds[0][1]). The second should be
        #       similar, within [bounds[1][0], bounds[1][1]). The third should be
        #       either 0, 1, 2, or 3. All values should be chosen uniform randomly.
        pass

    def recombine(self, mate, method, **kwargs):
        child = LinearGenotype()

        # TODO: Recombine geness of self with mate and assign to child's genes member variable
        assert method.casefold() in {'uniform', '1-point crossover', 'bonus'}
        if method.casefold() == 'uniform':
            # Perform uniform recombination
            pass
        elif method.casefold() == '1-point crossover':
            # Perform 1-point crossover
            pass
        elif method.casefold() == 'bonus':
            '''
            This is a red deliverable (i.e., bonus for anyone).

            Implement the bonus crossover operator as described in deliverable
            Red 1 of Assignment 1b.
            '''
            pass

        return child

    def mutate(self, bounds, bonus=None, **kwargs):
        copy = LinearGenotype()
        copy.genes = self.genes.copy()

        if not bonus:
            # TODO: Mutate genes of copy
            pass
        else:
            '''
            This is a red deliverable (i.e., bonus for anyone).

            Implement the bonus crossover operator as described in deliverable
            Red 1 of Assignment 1b.
            '''
            pass

        return copy

    @classmethod
    def initialization(cls, mu, *args, **kwargs):
        population = [cls() for _ in range(mu)]
        for i in range(len(population)):
            population[i].random_initialization(*args, **kwargs)
        return population