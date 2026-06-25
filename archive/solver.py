import os, sys, logging, numpy as np, time
from typing import List, Union, Tuple

start_time = time.perf_counter()  # Start the timer at the beginning of the script

# 1. Setup logging configuration to write to a file instead of the terminal
logging.basicConfig(
    filename='sudoku.log',
    filemode='a', # 'a' appends to the log file; use 'w' to overwrite every run
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def lean_exception_handler(exctype, value, traceback):
    # Prints just the error type and message, skipping the traceback entirely
    print(f"{exctype.__name__}: {value}", file=sys.stderr)

# Tell Python to use our clean handler instead of the default one
# sys.excepthook = lean_exception_handler

class SudoKuSolver:
    """ A class to solve Sudoku puzzles using mulitple strategies and parallel processing."""
    def __init__(self, board: List[List[int]]):
        try:
            self.board = np.array(board, dtype=int)
        except ValueError as e:
            logger.error(f"Error occurred while initializing board: {e}", exc_info=True)
            raise
        self.solved = False
        self.first_call = True  # Flag to indicate if it's the first call to validate_board

        
        

    def validate_board(self, board: np.ndarray = None) -> bool:
        """Validate the initial Sudoku board"""
        if board is None:
            board = self.board

        if self.first_call:
            if board.shape != (9, 9):
                logger.error(f"Invalid board size, got {board.shape[0]}x{board.shape[1]}.", exc_info=True)
                raise ValueError(f"Board must be 9x9, got {board.shape[0]}x{board.shape[1]}.")
                return False
            elif not np.all((board >= 0) & (board <= 9)):
                logger.error("Board contains invalid values. All values must be between 0 and 9.", exc_info=True)
                raise ValueError("Board contains invalid values. All values must be between 0 and 9.")
                return False
            elif self.validate_matrix(matrix=board) is not True:
                logger.error(f"Board contains duplicate values in rows, columns, or 3x3 subgrids. {self.validate_matrix(matrix=board)}", exc_info=True)
                raise ValueError("Board contains duplicate values in rows, columns, or 3x3 subgrids.")
                return False
            else:
                logger.info("Board validation successful.")
                print("Board validation successful and is loaded. \n","*"*60)
                return True
        else:
            if not self.validate_matrix(matrix=board):
                return False
            else:
                return True

        
    # def validate_matrix(self, matrix: np.ndarray) -> bool:
    #     """Check for duplicates in all 3x3 subgrids using list comprehension."""
    #     return all(
    #         len(x_mod := matrix[r:r+3, c:c+3].flatten()[matrix[r:r+3, c:c+3].flatten() > 0]) 
    #         == len(np.unique(x_mod))
    #         for r in (0, 3, 6) for c in (0, 3, 6)
    #     )

    def validate_matrix(self, matrix: np.ndarray) -> Union[bool, Tuple[int, int]]:
        """Check for duplicates in 3x3 subgrids and return error coordinates if found."""
        
        for i in range(9):
            row = matrix[i, matrix[i, :] > 0]
            col = matrix[matrix[:, i] > 0, i]
            if len(row) != len(np.unique(row)) or len(col) != len(np.unique(col)):
                return (i, i)        
        
        for r in (0, 3, 6):
            for c in (0, 3, 6):
                # Extract, flatten, and filter non-zero elements in one step
                if len(subgrid := matrix[r:r+3, c:c+3].flatten()[matrix[r:r+3, c:c+3].flatten() > 0]) != len(np.unique(subgrid)):
                    return r, c  # Return the starting row and column of the invalid 3x3 subgrid
                

        return True

    def solve_bruteforce(self) -> bool:
        """Solve the Sudoku puzzle using a brute-force backtracking algorithm."""
        empty = self.find_empty_location()
        if not empty:
            self.solved = True
            return True  # Puzzle solved
        row, col = empty

        for num in range(1, 10):
            self.board[row][col] = num
            if self.validate_board(self.board) is True:
                if self.solve_bruteforce():
                    return True
                self.board[row][col] = 0
        return False
                
    def find_empty_location(self):
        """Find an empty location in the Sudoku board."""
        return next(((i,j) for i in range(9) for j in range(9) if self.board[i][j] == 0),None)

def main():
    # Example usage
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
    solver.first_call=False
    solver.solve_bruteforce()
    if solver.solved:
        print(f"Solved Board: \n{solver.board} \n","*"*60)
    else:
        print("No solution exists for the given Sudoku puzzle.")    
    end_time = time.perf_counter()  # Stop the timer
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    # return None

if __name__ == "__main__":
    main()


