# solver.py
import os, sys, logging, numpy as np, time
from typing import List, Union, Tuple

logging.basicConfig(
    filename='sudoku.log',
    filemode='a',
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SudoKuSolver:
    """ A class to solve Sudoku puzzles using backtracking."""
    def __init__(self, board: List[List[int]]):
        try:
            self.board = np.array(board, dtype=int)
        except ValueError as e:
            logger.error(f"Error occurred while initializing board: {e}", exc_info=True)
            raise

        self.solved = False
        self.first_call = True  
        self.validate_board()

    def validate_board(self, board: np.ndarray = None) -> bool:
        if board is None:
            board = self.board

        if self.first_call:
            if board.shape != (9, 9):
                raise ValueError(f"Board must be 9x9, got {board.shape[0]}x{board.shape[1]}.")
            elif not np.all((board >= 0) & (board <= 9)):
                raise ValueError("Board contains invalid values.")
            elif self.validate_matrix(matrix=board) is not True:
                raise ValueError("Board contains duplicate values.")
            else:
                return True
        else:
            return self.validate_matrix(matrix=board) is True

    def validate_matrix(self, matrix: np.ndarray) -> Union[bool, Tuple[int, int]]:
        for i in range(9):
            row = matrix[i, matrix[i, :] > 0]
            col = matrix[matrix[:, i] > 0, i]
            if len(row) != len(np.unique(row)) or len(col) != len(np.unique(col)):
                return (i, i)

        for r in (0, 3, 6):
            for c in (0, 3, 6):
                subgrid = matrix[r:r+3, c:c+3].flatten()
                vals = subgrid[subgrid > 0]
                if len(vals) != len(np.unique(vals)):
                    return r, c
        return True
                
    def find_empty_location(self):
        return next(((i,j) for i in range(9) for j in range(9) if self.board[i][j] == 0), None)

    # ---> NEW METHOD FOR FASTAPI WEBSOCKET STREAMING <---
    def solve_generator(self):
        """Yields the board state at each step of the backtracking."""
        empty = self.find_empty_location()
        if not empty:
            self.solved = True
            return  # Puzzle solved, stop the generator
        
        row, col = empty

        for num in range(1, 10):
            self.board[row][col] = num
            
            if self.validate_board(self.board):
                # Yield the numpy array as a standard list for JSON serialization
                yield self.board.tolist()
                
                # Recurse through the generator
                yield from self.solve_generator()
                
                # If recursion flagged as solved, bubble up the exit
                if self.solved:
                    return
            
            # Backtrack
            self.board[row][col] = 0
            yield self.board.tolist()