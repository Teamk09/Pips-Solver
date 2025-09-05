import numpy as np
import time
from typing import List, Tuple, Dict, Any

LOG_INTERVAL = 50000

def solve_puzzle(board_size: int, dominoes: List[Tuple[int, int]], regions: Dict[str, Any], active_cells: List[Tuple[int, int]]):
    # Sets everything in the board as a -2 at first which means we won't consider that cell for the solution
    board = np.full((board_size, board_size), -2, dtype=int)
    
    # -1 means empty but active
    for r, c in active_cells:
        board[r, c] = -1
        
    used_dominoes = [False] * len(dominoes)
    active_cells_set = set(active_cells)
    step_counter = [0]
    start_time = time.time()

    print("--- Solver Started ---")
    print(f"Board Size: {board_size}x{board_size}, Dominoes: {len(dominoes)}, Active Cells: {len(active_cells)}")

    if backtrack(board, dominoes, used_dominoes, regions, active_cells_set, step_counter, start_time):
        end_time = time.time()
        print(f"--- Solution Found in {end_time - start_time:.2f} seconds ---")
        print(f"Total steps taken: {step_counter[0]:,}")
        return board
    else:
        end_time = time.time()
        print(f"--- No Solution Found after {end_time - start_time:.2f} seconds ---")
        print(f"Total steps explored: {step_counter[0]:,}")
        return None

def find_most_constrained_empty_cell(board: np.ndarray, regions: Dict[str, Any]) -> Tuple[int, int]:
    candidate_regions = []
    for data in regions.values():
        unfilled_cells = [cell for cell in data['cells'] if board[cell[0], cell[1]] == -1]
        if unfilled_cells:
            candidate_regions.append((len(unfilled_cells), unfilled_cells[0]))

    if candidate_regions:
        candidate_regions.sort()
        return candidate_regions[0][1]

    # Fallback for any active cells not in a region (should not happen in valid puzzles)
    for r in range(len(board)):
        for c in range(len(board)):
            if board[r,c] == -1: return r,c
    
    return None, None


def check_final_board(board: np.ndarray, regions: Dict[str, Any]) -> bool:
    for data in regions.values():
        cell_coords, rule, required_value = data['cells'], data['rule'], float(data.get('value', 0))
        if not cell_coords: continue
        values = [board[r,c] for r,c in cell_coords]
        current_sum = sum(values)

        if len(values) == 1:
            pip_value = values[0]
            if (rule == '>' and not pip_value > required_value) or \
               (rule == '<' and not pip_value < required_value) or \
               (rule == '∑' and not pip_value == required_value) or \
               (rule in ['=', '≠']): return False
            continue

        if (rule == '=' and len(set(values)) > 1) or \
           (rule == '≠' and len(set(values)) != len(values)) or \
           (rule == '>' and current_sum <= required_value) or \
           (rule == '<' and current_sum >= required_value) or \
           (rule == '∑' and current_sum != required_value): return False
    return True

def is_path_still_viable(board: np.ndarray, regions: Dict[str, Any]) -> bool:
    for data in regions.values():
        cell_coords, rule, required_value = data['cells'], data['rule'], float(data.get('value', 0))
        if not cell_coords: continue
        placed_values = [board[r,c] for r,c in cell_coords if board[r,c] != -1]
        if not placed_values: continue

        if len(cell_coords) == 1:
            pip_value = placed_values[0]
            if (rule == '>' and not pip_value > required_value) or \
               (rule == '<' and not pip_value < required_value) or \
               (rule == '∑' and not pip_value == required_value) or \
               (rule in ['=', '≠']): return False
            continue
        
        current_sum = sum(placed_values)
        if (rule == '=' and len(set(placed_values)) > 1) or \
           (rule == '≠' and len(set(placed_values)) != len(placed_values)) or \
           (rule == '<' and current_sum >= required_value) or \
           (rule == '∑' and current_sum > required_value): return False
    return True

def backtrack(board: np.ndarray, dominoes: List[Tuple[int, int]], used_dominoes: List[bool], regions: Dict[str, Any], active_cells_set: set, step_counter: list, start_time: float) -> bool:
    step_counter[0] += 1
    if step_counter[0] % LOG_INTERVAL == 0:
        elapsed = time.time() - start_time
        print(f"  ... still solving, steps: {step_counter[0]:,}, time: {elapsed:.1f}s")

    r, c = find_most_constrained_empty_cell(board, regions)
    if r is None:
        return check_final_board(board, regions)

    for i in range(len(dominoes)):
        if used_dominoes[i]: continue

        domino = dominoes[i]
        used_dominoes[i] = True

        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_r, next_c = r + dr, c + dc

            if 0 <= next_r < len(board) and 0 <= next_c < len(board) and board[next_r, next_c] == -1:
                
                for p1, p2 in [domino, (domino[1], domino[0])]:
                    #duplicates
                    if p1 == p2 and domino[0] != domino[1]: continue
                    
                    board[r, c], board[next_r, next_c] = p1, p2
                    if is_path_still_viable(board, regions) and backtrack(board, dominoes, used_dominoes, regions, active_cells_set, step_counter, start_time):
                        return True
                
                board[r, c], board[next_r, next_c] = -1, -1

        used_dominoes[i] = False

    return False