from os import path
from board import *
import copy
import functools
import heapq

# boards = from_file("jams_posted.txt")

def get_successors(state):
    """
    Return a list containing the successor states of the given state.
    The states in the list may be in any arbitrary order.

    :param state: The current state.
    :type state: State
    :return: The list of successor states.
    :rtype: List[State]
    """
    hfn  = state.hfn
    f = state.f
    depth = state.depth
    board = state.board
    grid = board.grid
    cars = board.cars
    name = board.name
    size = board.size

    new_states = []
    for i in range(len(cars)): 
        cur_car = cars[i]
        fix = cur_car.fix_coord
        var = cur_car.var_coord
        ori = cur_car.orientation
        length = cur_car.length
        if ori == "h":
            # fix is y-coord 
            # var is x-coord (need to consider)
            for pos in range(var - 1, -1, -1):
                if grid[fix][pos] == ".":
                    #print("position:[", fix, ",", pos, "] is ok")
                    newCar = copy.deepcopy(cur_car)
                    newCar.var_coord = pos
                    newCars = copy.deepcopy(cars)
                    newCars[i] = newCar
                    newBoard = Board(name, size, newCars)
                    new_f = hfn(newBoard) + depth + 1
                    newState = State(newBoard, hfn, new_f, depth+1, state)
                    new_states.append(newState)
                else:
                    break
            for pos in range(var + length, 6):
                if grid[fix][pos] == ".":
                    #print("position:[", fix, ",", pos, "] is ok")
                    newCar = copy.deepcopy(cur_car)
                    newCar.var_coord = pos + 1 - length
                    newCars = copy.deepcopy(cars)
                    newCars[i] = newCar
                    newBoard = Board(name, size, newCars)
                    new_f = hfn(newBoard) + depth + 1
                    newState = State(newBoard, hfn, new_f, depth+1, state)
                    new_states.append(newState)
                else:
                    break
        elif ori == "v":
            # fix is x-coord 
            # var is y-coord (need to consider)
            for pos in range(var - 1, -1, -1):
                if grid[pos][fix] == ".":
                    #print("position:[", pos, ",", fix, "] is ok")
                    newCar = copy.deepcopy(cur_car)
                    newCar.var_coord = pos
                    newCars = copy.deepcopy(cars)
                    newCars[i] = newCar
                    newBoard = Board(name, size, newCars)
                    new_f = hfn(newBoard) + depth + 1
                    newState = State(newBoard, hfn, new_f, depth+1, state)
                    new_states.append(newState)
                else:
                    break
            for pos in range(var + length, 6):
                if grid[pos][fix] == ".":
                    #print("position:[", pos, ",", fix, "] is ok")
                    newCar = copy.deepcopy(cur_car)
                    newCar.var_coord = pos + 1 - length
                    newCars = copy.deepcopy(cars)
                    newCars[i] = newCar
                    newBoard = Board(name, size, newCars)
                    new_f = hfn(newBoard) + depth + 1
                    newState = State(newBoard, hfn, new_f, depth+1, state)
                    new_states.append(newState)
                else:
                    break
    return new_states

def is_goal(state):
    """
    Returns True if the state is the goal state and False otherwise.

    :param state: the current state.
    :type state: State
    :return: True or False
    :rtype: bool
    """
    board = state.board
    return board.grid[2][5] == ">"

def get_path(state):
    """
    Return a list of states containing the nodes on the path 
    from the initial state to the given state in order.

    :param state: The current state.
    :type state: State
    :return: The path.
    :rtype: List[State]
    """
    path = []
    cur_state = state
    while cur_state != None:
        path.insert(0, cur_state)
        cur_state = cur_state.parent
    return path


def blocking_heuristic(board):
    """
    Returns the heuristic value for the given board
    based on the Blocking Heuristic function.

    Blocking heuristic returns zero at any goal board,
    and returns one plus the number of cars directly
    blocking the goal car in all other states.

    :param board: The current board.
    :type board: Board
    :return: The heuristic value.
    :rtype: int
    """
    grid = board.grid
    # if it is goal state, return 0
    if grid[2][5] == ">":
        return 0
    # if it is not goal state
    block = 1 
    right = 0
    for i in range(1,6):
        if grid[2][i] == ">":
            right = i
        elif grid[2][i] == "^" or grid[2][i] == "|" or grid[2][i] == "v":
            if i > right:
                block = block + 1
    return block

def advanced_heuristic(board):
    """
    An advanced heuristic of your own choosing and invention.

    :param board: The current board.
    :type board: Board
    :return: The heuristic value.
    :rtype: int
    """
    """
    idea: advanced heuristic function returns zero at any goal board,
    and similar to blocking_heuristic, we add 1 for each blocking car.
    and we add min of cars blocks blocking cars upper or below
    """
    grid = board.grid
    cars = board.cars
    # if it is goal state, return 0
    if grid[2][5] == ">":
        return 0
    # if it is not goal state find blocking cars
    block_col = []
    right = 6
    for i in range(1,6):
        if grid[2][i] == ">":
            right = i
        elif grid[2][i] == "^" or grid[2][i] == "|" or grid[2][i] == "v":
            if i > right:
                block_col.append(i)
    #we find the blocking cars
    blocking_cars = []
    blocking_cars_top = []
    blocking_cars_bottom = []
    for car in cars:
        if car.is_goal:
            continue
        if car.orientation == "v":
            if car.fix_coord in block_col:
                if car.var_coord + car.length < 2:
                    blocking_cars_top.append(car)
                elif car.var_coord > 2:
                    blocking_cars_bottom.append(car)
                else:
                    blocking_cars.append(car)
        elif car.orientation == "h":
            found = False
            for i in range(car.var_coord, car.var_coord + car.length):
                if i in block_col:
                    if found:
                        break
                    elif car.fix_coord < 2:
                        blocking_cars_top.append(car)
                        found = True
                    else:
                        blocking_cars_bottom.append(car)
                        found = True
    return 1 + len(blocking_cars) + min(len(blocking_cars_top), len(blocking_cars_bottom))

def compare_dfs(state_a, state_b):
    if not state_a.f == state_b.f:
        return state_b.f - state_a.f 
    return state_b.id - state_a.id

def in_explored(explored, state):
    for _state in explored:
        if state.board == _state.board:
            return True
    return False

def dfs(init_board):
    """
    Run the DFS algorithm given an initial board.

    If the function finds a goal state, it returns a list of states representing
    the path from the initial state to the goal state in order and the cost of
    the solution found.
    Otherwise, it returns am empty list and -1.

    :param init_board: The initial board.
    :type init_board: Board
    :return: (the path to goal state, solution cost)
    :rtype: List[State], int
    """
    # lec03 slides 38
    init_state = State(init_board, zero_heuristic, 0, 0)
    # frontier is a stack of states (in DFS), LIFO
    frontier = [init_state]
    # frontier = get_successors(init_state)
    # frontier.sort(key=functools.cmp_to_key(compare_dfs))
    explored = [] # a set of nodes(states)
    while frontier:
        new_state = frontier.pop() # select and remove path from frontier
        if not in_explored(explored, new_state):
            explored.append(new_state)
            if is_goal(new_state):
                path = get_path(new_state)
                return path, new_state.depth
            else:
                neighbours = get_successors(new_state)
                neighbours.sort(key=functools.cmp_to_key(compare_dfs))
                frontier.extend(neighbours)
    return [], -1

def in_explored(explored, state):
    for _state in explored:
        if state.f >= _state.f and state.id == _state.id:
            return True
    return False

def a_star(init_board, hfn):
    """
    Run the A_star search algorithm given an initial board and a heuristic function.

    If the function finds a goal state, it returns a list of states representing
    the path from the initial state to the goal state in order and the cost of
    the solution found.
    Otherwise, it returns am empty list and -1.

    :param init_board: The initial starting board.
    :type init_board: Board
    :param hfn: The heuristic function.
    :type hfn: Heuristic
    :return: (the path to goal state, solution cost)
    :rtype: List[State], int
    """
    init_state = State(init_board, hfn, hfn(init_board), 0)
    num_states = 0
    # frontier is a priority queue in A star
    frontier = [(init_state.f, init_state.id, 0, init_state)]
    heapq.heapify(frontier)

    explored = [] # a set of nodes(boards)
    while frontier:
        f, id, parentId, new_state = heapq.heappop(frontier) # select and remove path from frontier
        if not in_explored(explored, new_state):
            num_states = num_states + 1
            explored.append(new_state)
            if is_goal(new_state):
                path = get_path(new_state)
                return path, new_state.depth
            else:
                neighbours = get_successors(new_state)
                for neighbour in neighbours:
                    heapq.heappush(frontier, (neighbour.f, neighbour.id, neighbour.parent.id, neighbour))
    return [], -1

# i = 0
# for test_board in boards:
#     i = i + 1
#     print("Jam-",i)
#     test_board.display()
#     path1, cost1, num_state1 = a_star(test_board, blocking_heuristic)
#     print("# of states:", num_state1)
#     print("cost of blocking_heuristic:",cost1)
#     path2, cost2, num_state2 = a_star(test_board, advanced_heuristic)
#     print("# of states : ", num_state2)
#     print("cost of advanced_heuristic:",cost2)
#     if num_state1 >= num_state2:
#         print("advanced heuristic dominates the blocking heuristic")

