
# tree_genotype.py
import random
from typing import Literal, Tuple
from copy import deepcopy
from execution import nonterm_to_func, term_to_func
from functools import cache

class TreeGenotype():
    def __init__(self, **kwargs):
        self.fitness = None
        self.genes = ParseTree(**kwargs)


    @classmethod
    def initialization(cls, mu, depth_limit, c_range, **kwargs):
        population = [cls(**kwargs) for _ in range(mu)]

        for i in range(len(population) // 2):
            depth = random.uniform(1,depth_limit)
            population[i].genes.initialize(depth, 'full', c_range)

        for i in range(len(population) // 2, len(population)):
            depth = random.uniform(1,depth_limit)
            population[i].genes.initialize(depth, 'grow', c_range)

        # 2a TODO: Initialize genes member variables of individuals
        #          in population using ramped half-and-half.
        #          Pass **kwargs to your functions to give them
        #          the sets of terminal and nonterminal primitives.

        return population
    
    def execute(self, player, state):
        return self.genes.executeTree(player, state)


    def to_string(self):
        # 2a TODO: Return a string representing self.genes in the required format.
        return self.genes.requiredString()
        # return 'Unimplemented'


    def recombine(self, mate, depth_limit, **kwargs):
        child = self.__class__()

        # 2b TODO: Recombine genes of mate and genes of self to
        #          populate child's genes member variable.
        #          We recommend using deepcopy, but also recommend
        #          that you deepcopy the minimal amount possible.

        return child


    def mutate(self, depth_limit, **kwargs):
        mutant = self.__class__()
        mutant.genes = deepcopy(self.genes)

        # 2b TODO: Mutate mutant.genes to produce a modified tree.

        return mutant
    
class ParseTree:
    def __init__(self, terminals, nonterminals, **kwargs):
        self.terminals = list(terminals)
        self.nonterminals = list(nonterminals)
        assert len(set(terminals).intersection(set(nonterminals))) == 0
        self.root = None
    
    def initialize(self, depth_limit: int, method: Literal['full'] | Literal['grow'] = 'full', c_range: Tuple[float,float] = (-2,2)):
        def randomNode(useTerminal=None):
            '''Picks a random node from whichever set is chosen
            
            returns (bool terminal, node with value from set)
            '''
            if useTerminal is None:
                useTerminal = random.random() < 0.5
            if useTerminal:
                choice = random.choice(self.terminals)
                if choice == 'C':
                    choice = random.uniform(*c_range)
                return True, TreeNode(choice)
            choice = random.choice(self.nonterminals)
            if choice == 'C':
                choice = random.uniform(*c_range)
            return False, TreeNode(choice)
            
        def recGrow(curr: TreeNode, depth=0):
            if depth >= depth_limit:
                # we're right before depth limit. only use terminals
                _, curr = randomNode(useTerminal=True)
                return curr
            else:
                isTerm, curr = randomNode()
                if not isTerm:
                    curr.left = recGrow(curr.left, depth + 1)
                    curr.right = recGrow(curr.right, depth + 1)
                return curr

        def recFull(curr: TreeNode, depth=0):
            if depth >= depth_limit:
                # we're right before depth limit. only use terminals
                _, curr = randomNode(useTerminal=True)
                return curr
            else:
                # not at depth limit, use nonterminals
                _, curr = randomNode(useTerminal=False)
                curr.left = recFull(curr.left, depth + 1)
                curr.right = recFull(curr.right, depth + 1)
                return curr
        
        if method == 'full':
            self.root = recFull(self.root)
        else:
            # arbitrary decision by assignment authors to disallow trees with only 1 node
            _, self.root = randomNode(useTerminal=False)
            self.root.left = recGrow(self.root.left, depth=1)
            self.root.right = recGrow(self.root.right, depth=1)

    def requiredString(self):
        out = []
        def rec(curr, depth=0):
            # update to python 3.12 to make the quotes less hellish :)
            out.append(f'''{''.join(["|"] * depth)}{str(curr)}\n''')
            if curr.left:
                rec(curr.left, depth+1)
            if curr.right:
                rec(curr.right, depth+1)
        rec(self.root)
        return ''.join(out)
    
    def executeTree(self, player:str, state:dict):
        @cache
        def localCachedExecute(terminal):
            return term_to_func[terminal](player,state)
        
        def recExecute(t: TreeNode):
            if not t.left and not t.right:
                if type(t.val) == str:
                    # print("Func", t)
                    return localCachedExecute(t.val)
                return t.val
            else:
                # as a special feature of these trees, we always 
                # have both a left and right
                left = recExecute(t.left)
                right = recExecute(t.right)
                return nonterm_to_func[t.val](left, right)
        return recExecute(self.root)
    
    def __str__(self):
        out = []
        def rec(curr):
            if not curr.left and not curr.right:
                out.append(str(curr))
                return
            
            out.append('(')
            if curr.left:
                rec(curr.left)
            out.append(str(curr))
            if curr.right:
                rec(curr.right)
            out.append(')')
        rec(self.root)
        return ' '.join(out)

class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    def __str__(self):
        if type(self.val) is str:
            return self.val
        return f"{self.val:.3f}"
    
