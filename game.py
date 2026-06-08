import string
from dataclasses import dataclass
from typing import List, Tuple, Optional

WALLS_UP = {2, 6, 7}
WALLS_DOWN = {4, 5, 8}
WALLS_LEFT = {1, 5, 6}
WALLS_RIGHT = {3, 7, 8}
BLOCKED = {9}

@dataclass(frozen=True)
class Robot:
    id: str
    color: str
    r: int
    c: int

@dataclass(frozen=True)
class Target:
    r: int
    c: int
    color: str

@dataclass(frozen=True)
class GameState:
    robots: Tuple[Robot, ...]
    
    def __post_init__(self):
        # Precomputación de tupla de enteros para velocidad crítica de hash y comparación
        object.__setattr__(self, '_coords', tuple((r.r, r.c) for r in self.robots))
    
    def __hash__(self):
        return hash(self._coords)
        
    def __eq__(self, other):
        if not isinstance(other, GameState): return False
        return self._coords == other._coords

    def get_robot_by_color(self, color: str) -> Optional[Robot]:
        for robot in self.robots:
            if robot.color.lower() == color.lower(): return robot
        return None

class Board:
    def __init__(self, grid: List[List[int]], target: Target):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.target = target

    def is_valid_pos(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols

    def can_move(self, r: int, c: int, dr: int, dc: int, coords: tuple) -> bool:
        if self.grid[r][c] in BLOCKED: return False
        nr, nc = r + dr, c + dc
        if not (0 <= nr < self.rows and 0 <= nc < self.cols): return False
        if self.grid[nr][nc] in BLOCKED: return False
        if (nr, nc) in coords: return False

        if dr == -1:
            if self.grid[r][c] in WALLS_UP or self.grid[nr][nc] in WALLS_DOWN: return False
        elif dr == 1:
            if self.grid[r][c] in WALLS_DOWN or self.grid[nr][nc] in WALLS_UP: return False
        elif dc == -1:
            if self.grid[r][c] in WALLS_LEFT or self.grid[nr][nc] in WALLS_RIGHT: return False
        elif dc == 1:
            if self.grid[r][c] in WALLS_RIGHT or self.grid[nr][nc] in WALLS_LEFT: return False
            
        return True

    def move_robot(self, state: GameState, robot_idx: int, direction: str) -> Optional[GameState]:
        dr, dc = 0, 0
        if direction == 'U': dr, dc = -1, 0
        elif direction == 'D': dr, dc = 1, 0
        elif direction == 'L': dr, dc = 0, -1
        elif direction == 'R': dr, dc = 0, 1

        robot = state.robots[robot_idx]
        r, c = robot.r, robot.c
        
        moved = False
        # Deslizamiento usando lookup directo en la tupla sin recrear sets en memoria
        while self.can_move(r, c, dr, dc, state._coords):
            r += dr
            c += dc
            moved = True
            
        if not moved: return None
            
        new_robots = list(state.robots)
        new_robots[robot_idx] = Robot(robot.id, robot.color, r, c)
        return GameState(tuple(new_robots))

    def is_goal(self, state: GameState) -> bool:
        for robot in state.robots:
            if robot.r == self.target.r and robot.c == self.target.c:
                if self.target.color.lower() == "multicolor" or robot.color.lower() == self.target.color.lower():
                    return True
        return False

def load_level(filepath: str) -> Tuple[Board, GameState]:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    grid = []
    robot_lines = []
    target_line = lines[-1]
    
    for line in lines[:-1]:
        if " " in line: robot_lines.append(line)
        else: grid.append([int(char) for char in line])

    robots = []
    for i, r_line in enumerate(robot_lines):
        parts = r_line.split()
        robots.append(Robot(id=string.ascii_uppercase[i], color=parts[2], r=int(parts[0]), c=int(parts[1])))
        
    robots.sort(key=lambda x: x.id)
    t_parts = target_line.split()
    target = Target(r=int(t_parts[0]), c=int(t_parts[1]), color=t_parts[2])
    
    return Board(grid, target), GameState(tuple(robots))

def print_board(board: Board, state: GameState):
    robot_map = {(r.r, r.c): r for r in state.robots}
    print("-" * (board.cols * 4 + 1))
    for r in range(board.rows):
        row_str = "|"
        for c in range(board.cols):
            cell = board.grid[r][c]
            if (r, c) in robot_map: symbol = robot_map[(r, c)].id
            elif r == board.target.r and c == board.target.c: symbol = "X"
            elif cell == 9: symbol = "█"
            else: symbol = " "
            right_wall = "|" if cell in WALLS_RIGHT else " "
            row_str += f" {symbol} {right_wall}"
        print(row_str)
        sub_row = "+"
        for c in range(board.cols):
            cell = board.grid[r][c]
            bottom_wall = "---" if cell in WALLS_DOWN or r == board.rows - 1 else "   "
            sub_row += f"{bottom_wall}+"
        print(sub_row)
