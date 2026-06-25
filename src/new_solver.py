import os, sys, logging, numpy as np, time
from typing import List, Union, Tuple

start_time = time.perf_counter()

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

        # FIXED: Defined flags BEFORE validating the board
        self.solved = False
        self.first_call = True  

        self.validate_board()

    def validate_board(self, board: np.ndarray = None) -> bool:
        """Validate the initial Sudoku board"""
        if board is None:
            board = self.board

        if self.first_call:
            if board.shape != (9, 9):
                logger.error(f"Invalid board size, got {board.shape[0]}x{board.shape[1]}.", exc_info=True)
                raise ValueError(f"Board must be 9x9, got {board.shape[0]}x{board.shape[1]}.")
            elif not np.all((board >= 0) & (board <= 9)):
                logger.error("Board contains invalid values. All values must be between 0 and 9.", exc_info=True)
                raise ValueError("Board contains invalid values. All values must be between 0 and 9.")
            elif self.validate_matrix(matrix=board) is not True:
                logger.error("Board contains duplicate values.", exc_info=True)
                raise ValueError("Board contains duplicate values in rows, columns, or 3x3 subgrids.")
            else:
                logger.info("Board validation successful.")
                print("Board validation successful and is loaded. \n","*"*60)
                return True
        else:
            return self.validate_matrix(matrix=board) is True

    def validate_matrix(self, matrix: np.ndarray) -> Union[bool, Tuple[int, int]]:
        """Check for duplicates in rows, columns, and 3x3 subgrids."""
        # Check rows and columns
        for i in range(9):
            row = matrix[i, matrix[i, :] > 0]
            col = matrix[matrix[:, i] > 0, i]
            if len(row) != len(np.unique(row)) or len(col) != len(np.unique(col)):
                return (i, i)

        # Check 3x3 subgrids
        for r in (0, 3, 6):
            for c in (0, 3, 6):
                subgrid = matrix[r:r+3, c:c+3].flatten()
                vals = subgrid[subgrid > 0]
                if len(vals) != len(np.unique(vals)):
                    return r, c
                    
        return True

    def solve_bruteforce(self) -> bool:
        """Solve the Sudoku puzzle using a backtracking algorithm."""
        empty = self.find_empty_location()
        if not empty:
            self.solved = True
            return True  # Puzzle solved
        
        row, col = empty

        # Try placing numbers 1 through 9
        for num in range(1, 10):
            self.board[row][col] = num
            
            # Check if this placement keeps the board valid
            if self.validate_board(self.board):
                # FIXED: Recursively try to solve the rest of the board
                if self.solve_bruteforce():
                    return True
            
            # FIXED: Backtrack if the number didn't lead to a solution
            self.board[row][col] = 0

        return False # Triggers backtracking in the previous stack frames
                
    def find_empty_location(self):
        """Find an empty location in the Sudoku board."""
        return next(((i,j) for i in range(9) for j in range(9) if self.board[i][j] == 0), None)

def main():
    # Example usage (Fixed duplicate 7 in the first row of your sample)
    board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    solver = SudoKuSolver(board)
    print(f"Initial Board: \n{solver.board} \n","*"*60)
    solver.first_call = False
    
    if solver.solve_bruteforce():
        print(f"Solved Board: \n{solver.board} \n","*"*60)
    else:
        print("No solution exists for the given Sudoku puzzle.")    
        
    end_time = time.perf_counter()
    print(f"Execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
