import time
import tracemalloc
from collections import deque
import heapq
from typing import List, Tuple, Dict, Optional, Any
from game import Board, GameState

class Node:
    def __init__(self, state: GameState, parent=None, action: str = "", cost: int = 0, depth: int = 0):
        self.state = state
        self.parent = parent
        self.action = action  
        self.cost = cost
        self.depth = depth

    def get_path(self) -> List[str]:
        path = []
        curr = self
        while curr.parent is not None:
            path.append(curr.action)
            curr = curr.parent
        return path[::-1]

def get_successors(board: Board, node: Node) -> List[Node]:
    successors = []
    for i, robot in enumerate(node.state.robots):
        for d in ['U', 'D', 'L', 'R']:
            new_state = board.move_robot(node.state, i, d)
            if new_state is not None:
                action = f"{robot.id}-{d}"
                successors.append(Node(new_state, node, action, node.cost + 1, node.depth + 1))
    return successors

def run_search(algo_func, board: Board, initial_state: GameState, **kwargs) -> Dict[str, Any]:
    tracemalloc.start()
    
    # Ejecuta el algoritmo
    result = algo_func(board, initial_state, **kwargs)
    
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    status = result.get("status", "Success")
    if status == "Success" and result["node"]:
        path = result["node"].get_path()
        cost = result["node"].cost
        depth = result["node"].depth
    else:
        path = []
        cost = "Timeout"
        depth = result.get("max_depth", 0)

    return {
        "path_to_goal": path,
        "cost_of_path": cost,
        "nodos_expandidos": result["expanded"],
        "profundidad_de_búsqueda": depth,
        "max_search_depth": result["max_depth"],
        "running_time": result.get("time_taken", 0.0),
        "max_ram_usage": peak / (1024 * 1024),
        "status": status
    }

def bfs(board: Board, initial_state: GameState, time_limit: float = 60.0) -> Dict:
    start_time = time.perf_counter()
    start_node = Node(initial_state)
    if board.is_goal(initial_state): 
        return {"node": start_node, "expanded": 0, "max_depth": 0, "status": "Success", "time_taken": time.perf_counter() - start_time}
    
    frontier = deque([start_node])
    explored = {initial_state}
    expanded = 0
    max_depth = 0
    
    while frontier:
        # CORTE POR TIEMPO: Si pasa de 60 segundos, aborta.
        if time.perf_counter() - start_time > time_limit:
            return {"node": None, "expanded": expanded, "max_depth": max_depth, "status": "Timeout", "time_taken": time.perf_counter() - start_time}
            
        node = frontier.popleft()
        expanded += 1
        
        for child in get_successors(board, node):
            max_depth = max(max_depth, child.depth)
            if child.state not in explored:
                if board.is_goal(child.state): 
                    return {"node": child, "expanded": expanded, "max_depth": max_depth, "status": "Success", "time_taken": time.perf_counter() - start_time}
                explored.add(child.state)
                frontier.append(child)
    return {"node": None, "expanded": expanded, "max_depth": max_depth, "status": "No Solution", "time_taken": time.perf_counter() - start_time}

def dfs(board: Board, initial_state: GameState, time_limit: float = 60.0) -> Dict:
    start_time = time.perf_counter()
    start_node = Node(initial_state)
    frontier = [start_node]
    explored = set()
    expanded = 0
    max_depth = 0
    
    while frontier:
        # CORTE POR TIEMPO: Si pasa de 60 segundos, aborta.
        if time.perf_counter() - start_time > time_limit:
            return {"node": None, "expanded": expanded, "max_depth": max_depth, "status": "Timeout", "time_taken": time.perf_counter() - start_time}
            
        node = frontier.pop()
        if board.is_goal(node.state): 
            return {"node": node, "expanded": expanded, "max_depth": max_depth, "status": "Success", "time_taken": time.perf_counter() - start_time}
            
        if node.state not in explored:
            explored.add(node.state)
            expanded += 1
            children = get_successors(board, node)
            for child in reversed(children):
                max_depth = max(max_depth, child.depth)
                if child.state not in explored: frontier.append(child)
    return {"node": None, "expanded": expanded, "max_depth": max_depth, "status": "No Solution", "time_taken": time.perf_counter() - start_time}

def h1_manhattan(board: Board, state: GameState) -> float:
    robot = state.get_robot_by_color(board.target.color)
    if not robot:
        dists = [abs(r.r - board.target.r) + abs(r.c - board.target.c) for r in state.robots]
        dist = min(dists) if dists else 0
    else: dist = abs(robot.r - board.target.r) + abs(robot.c - board.target.c)
    max_dist = board.rows + board.cols
    return dist / max_dist if max_dist > 0 else 0.0

def h2_straight_line(board: Board, state: GameState) -> float:
    robot = state.get_robot_by_color(board.target.color)
    if not robot: return 0.1
    if robot.r != board.target.r and robot.c != board.target.c: return 1.0
    return 0.1

def h3_blocking_robots(board: Board, state: GameState) -> float:
    robot = state.get_robot_by_color(board.target.color)
    if not robot: return 0.0
    blocks = 0
    min_r, max_r = min(robot.r, board.target.r), max(robot.r, board.target.r)
    min_c, max_c = min(robot.c, board.target.c), max(robot.c, board.target.c)
    for r2 in state.robots:
        if r2.id != robot.id:
            if min_r <= r2.r <= max_r and min_c <= r2.c <= max_c: blocks += 1
    return blocks / len(state.robots)

def h4_wall_estimation(board: Board, state: GameState) -> float:
    return min(1.0, h1_manhattan(board, state) * 1.3)

def h5_combined_distance(board: Board, state: GameState) -> float:
    total_dist = sum(abs(r.r - board.target.r) + abs(r.c - board.target.c) for r in state.robots)
    max_dist = (board.rows + board.cols) * len(state.robots)
    return total_dist / max_dist if max_dist > 0 else 0.0

def calculate_heuristic(board: Board, state: GameState, weights: List[float], num_heuristics: int) -> float:
    heuristics = [h1_manhattan(board, state), h2_straight_line(board, state), h3_blocking_robots(board, state), h4_wall_estimation(board, state), h5_combined_distance(board, state)]
    val = 0.0
    for i in range(num_heuristics):
        w = weights[i] if i < len(weights) else 1.0
        val += heuristics[i] * w
    return val

def astar(board: Board, initial_state: GameState, num_heuristics: int = 3, weights: List[float] = None, time_limit: float = 60.0) -> Dict:
    start_time = time.perf_counter()
    if weights is None: weights = [1.0] * num_heuristics
    start_node = Node(initial_state)
    counter = 0 
    frontier = []
    
    dir_map = {'U': 0, 'D': 1, 'L': 2, 'R': 3}
    h_val = calculate_heuristic(board, initial_state, weights, num_heuristics)
    heapq.heappush(frontier, (h_val, 0, 0, counter, start_node))
    g_score = {initial_state: 0}
    explored = set()
    expanded = 0
    max_depth = 0
    
    while frontier:
        # CORTE POR TIEMPO: Si pasa de 60 segundos, aborta.
        if time.perf_counter() - start_time > time_limit:
            return {"node": None, "expanded": expanded, "max_depth": max_depth, "status": "Timeout", "time_taken": time.perf_counter() - start_time}
            
        _, _, _, _, node = heapq.heappop(frontier)
        if board.is_goal(node.state): 
            return {"node": node, "expanded": expanded, "max_depth": max_depth, "status": "Success", "time_taken": time.perf_counter() - start_time}
        if node.state in explored: continue
            
        explored.add(node.state)
        expanded += 1
        
        for child in get_successors(board, node):
            max_depth = max(max_depth, child.depth)
            tentative_g = node.cost + 1
            if child.state not in g_score or tentative_g < g_score[child.state]:
                g_score[child.state] = tentative_g
                h = calculate_heuristic(board, child.state, weights, num_heuristics)
                f_score = tentative_g + h
                
                r_id, d_char = child.action.split('-')
                counter += 1
                heapq.heappush(frontier, (f_score, ord(r_id), dir_map[d_char], counter, child))
    return {"node": None, "expanded": expanded, "max_depth": max_depth, "status": "No Solution", "time_taken": time.perf_counter() - start_time}
