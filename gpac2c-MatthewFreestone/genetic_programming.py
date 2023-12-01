
# genetic_programming.py

from base_evolution import BaseEvolutionPopulation
import random

class GeneticProgrammingPopulation(BaseEvolutionPopulation):
    def generate_children(self):
        children = list()
        recombined_child_count = 0
        mutated_child_count = 0

        parents = self.parent_selection(self.population, self.num_children * 2, **self.parent_selection_kwargs)
        random.shuffle(parents)
        parent_pairs = list(zip(parents[::2], parents[1::2]))
        for p1, p2 in parent_pairs:
            if random.random() < self.mutation_rate:
                child = random.choice((p1,p2)).mutate(**self.mutation_kwargs)
                mutated_child_count += 1
            else:
                child = p1.recombine(p2, **self.recombination_kwargs)
                recombined_child_count += 1
            children.append(child)

        self.log.append(f'Number of children: {len(children)}')
        self.log.append(f'Number of recombinations: {recombined_child_count}')
        self.log.append(f'Number of mutations: {mutated_child_count}')

        return children


        # # Randomly select self.num_children * 2 parents using your selection algorithm
        # parents = self.parent_selection(self.population, self.num_children * 2, **self.parent_selection_kwargs)
        # random.shuffle(parents)

        # children = []
        # mutated_child_count = 0
        # parent_pairs = list(zip(parents[::2], parents[1::2]))
        # for p1, p2 in parent_pairs:
        #     child = p1.recombine(p2, **self.recombination_kwargs)
        #     if random.random() < self.mutation_rate:
        #         child = child.mutate(**self.mutation_kwargs)
        #         mutated_child_count += 1
        #     children.append(child)

        # self.log.append(f'Number of children: {len(children)}')
        # self.log.append(f'Number of mutations: {mutated_child_count}')

        # return children