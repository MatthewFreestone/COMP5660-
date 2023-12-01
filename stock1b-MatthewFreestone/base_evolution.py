
# base_evolution.py

import statistics
import random

class BaseEvolutionPopulation():
    def __init__(self, individual_class, mu, num_children,
                 mutation_rate, parent_selection, survival_selection,
                 problem=dict(), parent_selection_kwargs=dict(),
                 recombination_kwargs=dict(), mutation_kwargs=dict(),
                 survival_selection_kwargs=dict(), **kwargs):
        self.mu = mu
        self.num_children = num_children
        self.mutation_rate = mutation_rate
        self.parent_selection = parent_selection
        self.survival_selection = survival_selection
        self.parent_selection_kwargs = parent_selection_kwargs
        self.recombination_kwargs = recombination_kwargs
        self.mutation_kwargs = mutation_kwargs
        self.survival_selection_kwargs = survival_selection_kwargs

        self.log = []
        self.log.append(f'mu: {self.mu}')
        self.log.append(f'num_children: {self.num_children}')
        self.log.append(f'mutation rate: {self.mutation_rate}')
        self.log.append(f'parent selection: {self.parent_selection.__name__ }')
        self.log.append(f'parent selection kwargs: {self.parent_selection_kwargs}')
        self.log.append(f'survival selection: {self.survival_selection.__name__ }')
        self.log.append(f'survival selection kwargs: {self.survival_selection_kwargs}')
        self.log.append(f'recombination kwargs: {self.recombination_kwargs}')
        self.log.append(f'mutation kwargs: {self.mutation_kwargs}')

        self.population = individual_class.initialization(self.mu, **problem, **kwargs)
        self.evaluations = 0

        self.log.append(f'Initial population size: {len(self.population)}')


    def generate_children(self):
        # Randomly select self.num_children * 2 parents using your selection algorithm
        parents = self.parent_selection(self.population, self.num_children * 2, **self.parent_selection_kwargs)
        random.shuffle(parents)

        children = []
        mutated_child_count = 0
        parent_pairs = list(zip(parents[::2], parents[1::2]))
        for p1, p2 in parent_pairs:
            child = p1.recombine(p2, **self.recombination_kwargs)
            if random.random() < self.mutation_rate:
                child = child.mutate(**self.mutation_kwargs)
                mutated_child_count += 1
            children.append(child)

        self.log.append(f'Number of children: {len(children)}')
        self.log.append(f'Number of mutations: {mutated_child_count}')

        return children

    def survival(self):
        self.log.append(f'Pre-survival population size: {len(self.population)}')
        self.population = self.survival_selection(self.population, self.mu, **self.survival_selection_kwargs)
        self.log.append(f'Post-survival population size: {len(self.population)}')
