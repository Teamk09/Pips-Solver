import numpy as np
from typing import List, Tuple, Dict, Any

def solve_puzzle(board_size: int, dominoes: List[Tuple[int, int]], regions: Dict[str, Any], active_cells: List[Tuple[int, int]]):
    # Sets everything in the board as a -2 at first which means we won't consider that cell for the solution
    board = np.full((board_size, board_size), -2, dtype=int)
    
    # -1 means empty but active
    for r, c in active_cells:
        board[r, c] = -1
        
    used_dominoes = [False] * len(dominoes)
    
    # fast lookup
    active_cells_set = set(active_cells)

    if backtrack(board, dominoes, used_dominoes, regions, active_cells_set):
        return board
    else:
        return None

def find_empty_cell(board: np.ndarray) -> Tuple[int, int]:
    for r in range(len(board)):
        for c in range(len(board[r])):
            if board[r, c] == -1:
                return r, c
    return None, None

def check_all_regions(board: np.ndarray, regions: Dict[str, Any]) -> bool:
    # make sure we don't break any rules
    for region_id, data in regions.items():
        rule = data['rule']
        required_value = data.get('value', 0)
        cell_coords = data['cells']

        if not cell_coords:
            continue

        values = [board[r, c] for r, c in cell_coords]

        # this is for when we're looping through backtracking, should never appear in a solution
        if any(v < 0 for v in values):
            return False 

        if rule == '=':
            if len(set(values)) > 1: return False
        elif rule == '≠':
            if len(values) > 1 and len(set(values)) != len(values): return False
        elif rule == '>':
            if not all(v > required_value for v in values): return False
        elif rule == '<':
            if not all(v < required_value for v in values): return False
        elif rule == '∑':
            if sum(values) != required_value: return False
    return True

def backtrack(board: np.ndarray, dominoes: List[Tuple[int, int]], used_dominoes: List[bool], regions: Dict[str, Any], active_cells_set: set) -> bool:
    r, c = find_empty_cell(board)

    if r is None:
        return check_all_regions(board, regions)

    for i in range(len(dominoes)):
        if not used_dominoes[i]:
            domino = dominoes[i]
            
            # horizontal logic
            if c + 1 < len(board) and (r, c + 1) in active_cells_set and board[r, c + 1] == -1:
                used_dominoes[i] = True
                
                # 90 deg
                board[r, c], board[r, c + 1] = domino[0], domino[1]
                if backtrack(board, dominoes, used_dominoes, regions, active_cells_set):
                    return True

                # 270
                board[r, c], board[r, c + 1] = domino[1], domino[0]
                if backtrack(board, dominoes, used_dominoes, regions, active_cells_set):
                    return True
                
                # Backtrack
                board[r, c], board[r, c + 1] = -1, -1
                used_dominoes[i] = False

            # vertical logic
            if r + 1 < len(board) and (r + 1, c) in active_cells_set and board[r + 1, c] == -1:
                used_dominoes[i] = True
                
                # 0 deg
                board[r, c], board[r + 1, c] = domino[0], domino[1]
                if backtrack(board, dominoes, used_dominoes, regions, active_cells_set):
                    return True

                # 360
                if domino[0] != domino[1]: #slight speedup for dominos that are doubles (i.e. 6-6)
                    board[r, c], board[r + 1, c] = domino[1], domino[0]
                    if backtrack(board, dominoes, used_dominoes, regions, active_cells_set):
                        return True
                
                # Backtrack
                board[r, c], board[r + 1, c] = -1, -1
                used_dominoes[i] = False
    return False