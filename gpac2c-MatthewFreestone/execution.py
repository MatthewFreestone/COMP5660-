import random
INF_VALUE = 1e10

def safeDivide(a:float, b:float):
    assert type(a) == type(b) == float
    if b == 0:
        return 0.0 if a==0 else INF_VALUE
    return float(a/b)

def rand(a:float, b:float):
    return random.uniform(min(a,b), max(a,b))


nonterm_to_func = {
    "+": float.__add__,
    '-': float.__sub__,
    '*': float.__mul__,
    '/': safeDivide,
    'RAND': rand
}

def ghostDistance(player, state):
    dist_to_ghost = INF_VALUE
    my_loc = state['players'][player]
    for loc in (v for k,v in state['players'].items() if ('m' not in k) and (k != player)):
        dist = manhattan(my_loc, loc)
        dist_to_ghost = min(dist_to_ghost, dist)
    return float(dist_to_ghost)

def playerDistance(player, state):
    dist_to_player = INF_VALUE
    my_loc = state['players'][player]
    for loc in (v for k,v in state['players'].items() if ('m' in k) and (k != player)):
        dist = manhattan(my_loc, loc)
        dist_to_player = min(dist_to_player, dist)
    return float(dist_to_player)

def pillDistance(player, state):
    dist_to_pill = INF_VALUE
    my_loc = state['players'][player]
    for loc in state['pills']:
        dist = manhattan(my_loc, loc)
        dist_to_pill = min(dist_to_pill, dist)
    return float(dist_to_pill)

def fruitDistance(player, state):
    # the lower this distance is, generally the better
    # when no fruit, set it to some middle-of-the-road value like 100.
    dist_to_fruit = 100.0
    if state['fruit'] is None:
        return dist_to_fruit
    my_loc = state['players'][player]
    return float(manhattan(my_loc, state['fruit']))

def adjacentWalls(player, state):
    adj = 0
    x,y = state['players'][player]
    for dx, dy in ((0, 1), (1, 0), (0,-1), (-1, 0)):
        if 0 <= x+dx < len(state['walls']) and  0 <= y+dy < len(state['walls'][0]):
            if state['walls'][x+dx][y+dy]:
                adj += 1
    return float(adj)

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

term_to_func = {
    'G': ghostDistance,
    'P': pillDistance,
    'F': fruitDistance,
    'W': adjacentWalls,
    'M': playerDistance
}
