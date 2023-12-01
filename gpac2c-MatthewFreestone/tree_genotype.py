
# tree_genotype.py
# this should be the default. upsetting that it is not.
# allows forward references for typing
from __future__ import annotations
import random
from copy import deepcopy
from parse_tree import ParseTree, TreeNode



class TreeGenotype:
    genes: ParseTree
    base_fitness: float
    fitness: float

    def __init__(self, **kwargs):
        self.base_fitness = None
        self.fitness = None
        self.genes = None
        self.log = None

    @classmethod
    def initialization(cls, mu, depth_limit, c_range, **kwargs):
        population = [cls(**kwargs) for _ in range(mu)]

        for i in range(len(population) // 2):
            depth = random.uniform(1,depth_limit)
            population[i].genes = ParseTree(**kwargs)
            population[i].genes.initialize(depth, 'full', c_range)

        for i in range(len(population) // 2, len(population)):
            depth = random.uniform(1,depth_limit)
            population[i].genes = ParseTree(**kwargs)
            population[i].genes.initialize(depth, 'grow', c_range)

        return population
    
    def execute(self, player, state):
        return self.genes.executeTree(player, state)


    def to_string(self):
        # 2a TODO: Return a string representing self.genes in the required format.
        return self.genes.requiredString()
        # return 'Unimplemented'

    def recombine(self, mate: TreeGenotype, depth_limit, **kwargs):
        child = TreeGenotype()
        # because of my pointer nonsense, its gonna be slow.
        # using Cython would probably be better.
        child.genes = deepcopy(self.genes)

        # pick a random node on self and put all of mate at that node
        left_node_idx = random.randint(0, len(child.genes) - 1)
        right_node_idx = random.randint(0, len(mate.genes) - 1)
        # print(left_node_idx, right_node_idx)

        to_put, _ = mate.genes.getNthNode(right_node_idx)
        # print(to_put)
        # print(child.genes.getNthNode(left_node_idx))
        child.genes.setNthNode(left_node_idx, deepcopy(to_put))

        # very possible that tree is now above depth limit. Prune.

        child.genes.pruneToDepth(depth_limit)
        return child

    def mutate(self, depth_limit, **kwargs):
        mutant = self.__class__()
        mutant.genes = deepcopy(self.genes)
        mutation_idx = random.randint(0, len(mutant.genes)-1)
        # print(mutation_idx, mutant.genes.getNthNode(mutation_idx)[0])
        mutant.genes.subtreeMutate(mutation_idx, depth_limit)
        
        return mutant
    
