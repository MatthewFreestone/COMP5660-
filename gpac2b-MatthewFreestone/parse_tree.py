import random
from typing import Literal, Tuple, List
from execution import nonterm_to_func, term_to_func
from functools import cache

class TreeNode:
    def __init__(self, val, left=None, right=None, parent=None):
        self.val = val
        self.left = left
        self.right = right
        self.parent = parent
    def __str__(self):
        if type(self.val) is str:
            return self.val
        return f"{self.val:.3f}"
    def nodesBelow(self):
        total = 1
        if self.left: total += self.left.nodesBelow()
        if self.right: total += self.right.nodesBelow()
        return total    

class ParseTree:
    root: TreeNode
    size: int
    nonterminals: List[str]
    terminals: List[str]
    c_range: Tuple[float, float]

    def __init__(self, terminals: List[str], nonterminals: List[str], **kwargs):
        self.terminals = list(terminals)
        self.nonterminals = list(nonterminals)
        assert len(set(terminals).intersection(set(nonterminals))) == 0
        self.size = 0
        self.root = None
        self.c_range = None
    
    def _randomNode(self, useTerminal=None) -> Tuple[bool, TreeNode]:
            '''Picks a random node from whichever set is chosen
            
            returns (bool terminal, node with value from set)
            '''
            if useTerminal is None:
                useTerminal = random.random() < 0.5
            if useTerminal:
                choice = random.choice(self.terminals)
                if choice == 'C':
                    choice = random.uniform(*self.c_range)
                return True, TreeNode(choice)
            choice = random.choice(self.nonterminals)
            if choice == 'C':
                choice = random.uniform(*self.c_range)
            return False, TreeNode(choice)
    
    def _recGrow(self, depth_limit: int, depth=0) -> TreeNode:
        if depth >= depth_limit:
            # we're right before depth limit. only use terminals
            _, curr = self._randomNode(useTerminal=True)
            self.size += 1
            return curr
        else:
            isTerm, curr = self._randomNode()
            if not isTerm:
                curr.left = self._recGrow(depth_limit, depth + 1)
                curr.left.parent = curr

                curr.right = self._recGrow(depth_limit, depth + 1)
                curr.right.parent = curr
            self.size += 1
            return curr
    
    def _recFull(self, depth_limit: int, depth=0) -> TreeNode:
        if depth >= depth_limit:
            # we're right before depth limit. only use terminals
            _, curr = self._randomNode(useTerminal=True)
            self.size += 1
            return curr
        else:
            # not at depth limit, use nonterminals
            _, curr = self._randomNode(useTerminal=False)
            curr.left = self._recFull(depth_limit, depth + 1)
            curr.left.parent = curr
            curr.right = self._recFull(depth_limit, depth + 1)
            curr.right.parent = curr
            self.size += 1
            return curr

    
    def initialize(self, depth_limit: int, method: Literal['full'] | Literal['grow'] = 'full', c_range: Tuple[float,float] = (-2,2)):
        self.c_range = c_range        
        if method == 'full':
            self.root = self._recFull(depth_limit, depth=0)
        else:
            # arbitrary decision by assignment authors to disallow trees with only 1 node
            _, self.root = self._randomNode(useTerminal=False)
            self.size += 1
            self.root.left = self._recGrow(depth_limit, depth=1)
            self.root.left.parent = self.root
            self.root.right = self._recGrow(depth_limit, depth=1)
            self.root.right.parent = self.root


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
                    return localCachedExecute(t.val)
                return t.val
            else:
                # as a special feature of these trees, we always 
                # have both a left and right
                left = recExecute(t.left)
                right = recExecute(t.right)
                return nonterm_to_func[t.val](left, right)
        return recExecute(self.root)
    
    def getNthNode(self, n:int) -> Tuple[TreeNode, int]:
        '''returns TreeNode and depth of it'''
        assert 0 <= n < len(self)

        curr = self.root
        stack = []
        depth = 0
        i = 0
        while True:
            if curr is not None:
                stack.append((curr, depth))
                # could be None
                depth += 1
                curr = curr.left
            elif stack:
                curr, depth = stack.pop()
                if i == n:
                    return curr, depth
                i += 1
                depth += 1
                curr = curr.right

    def setNthNode(self, n:int, target):
        assert 0 <= n < len(self)
        curr = self.root
        stack = []
        i = 0
        last = ''
        while True:
            if curr is not None:
                stack.append((curr, last))
                # could be None
                curr = curr.left
                last = 'L'
            elif stack:
                curr, last = stack.pop()
                if i == n:
                    # we shouldn't allow the root to get replaced, as that would 
                    # allow 0 depth trees, so take the left or right randomly
                    if curr == self.root:
                        if random.random() < 0.5:
                            curr = curr.left
                            last = 'L'
                        else:
                            curr = curr.right
                            last = 'R' 
                    self.size -= curr.nodesBelow()
                    self.size += target.nodesBelow()
                    parent = curr.parent
                    if last == 'L':
                        parent.left = target
                        target.parent = parent
                    elif last == 'R':
                        parent.right = target
                        target.parent = parent
                    else:
                        raise 
                    break
                i += 1
                curr = curr.right
                last = 'R'

    def pruneToDepth(self, depth_limit: int):
        # do a dfs traversal. When we get too deep, 
        # dereference children and replace with terminal
        def recPrune(curr: TreeNode, depth=0):
            if curr is None:
                return None
            if depth == depth_limit:
                # we're right at depth limit. ensure only have terminals
                if curr.left is not None and curr.right is not None:
                    # curr is currently a non-terminal. We need to replace it.
                    self.size -= curr.nodesBelow()
                    parent = curr.parent
                    _, curr = self._randomNode(useTerminal=True)
                    curr.parent = parent

                return curr
            else:
                # not at depth limit, keep going down.
                curr.left = recPrune(curr.left, depth + 1)
                curr.right = recPrune(curr.right, depth + 1)
                return curr
        self.root = recPrune(self.root)
    
    def subtreeMutate(self, mutation_idx, depth_limit):
        target, depth = self.getNthNode(mutation_idx)
        tumor = self._recGrow(depth_limit, depth)
        # _recGrow increases size, and so does Nth node. Move down size first so we don't double count
        self.size -= tumor.nodesBelow()
        self.setNthNode(mutation_idx, tumor)
            
    def __str__(self):
        # out = [str(len(self))]
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

    def __len__(self) -> int:
        return self.root.nodesBelow()
        # return self.size

    def maxDepth(self) -> int:
        def subtreeDepth(node):
            if not node: return -1
            return 1 + max(subtreeDepth(node.left), subtreeDepth(node.right))
        return subtreeDepth(self.root)


