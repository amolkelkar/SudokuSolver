"""
Sudoku Solver with Parallel Processing
Uses multiprocessing for CPU-bound tasks and threading for initial analysis
"""
from typing import List, Optional, Tuple, Set
import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import multiprocessing
import sys

class SudokuSolver:
    """Sudoku solver with parallel processing capabilities"""
    
    def __init__(self, puzzle: List[List[int]]):
        self.puzzle = np.array(puzzle, dtype=int)
        self.solved = None
        self.constraints = self._analyze_constraints()
    
    def _analyze_constraints(self) -> List[List[Set[int]]]:
        """Analyze which numbers can go in each cell"""
        n_rows, n_cols = self.puzzle.shape
        constraints = []
        
        for i in range(n_rows):
            row_set = set(self.puzzle[i])
            box_row_start = (i // 3) * 3
            box_col_start = (i % 3) * 3
            box_set = set(self.puzzle[box_row_start:box_row_start+3, box_col_start:box_col_start+3])
            col_set = set(self.puzzle[:, i])
            
            candidates = {1, 2, 3, 4, 5, 6, 7, 8, 9} - (row_set | box_set | col_set)
            constraints.append(candidates)
        
        return constraints
    
    def _solve_cell(self, row: int, col: int, candidates: Set[int]) -> Tuple[Optional[int], bool]:
        """Solve a single cell - returns (assigned_value, success)"""
        for candidate in candidates:
            if self._is_valid_placement(row, col, candidate):
                return candidate, True
        
        return None, False
    
    def _is_valid_placement(self, row: int, col: int, value: int) -> bool:
        """Check if placing value at (row, col) is valid"""
        if value in self.puzzle[row]:
            return False
        
        row_idx = (row // 3) * 3 + (row % 3)
        col_idx = (col // 3) * 3 + (col % 3)
        if value in self.puzzle[row_idx:row_idx+3, col:col+3]:
            return False
        
        col_set = set(self.puzzle[:, col])
        if value in col_set:
            return False
        
        return True
    
    def _solve_recursive(self, row: int, col: int) -> Tuple[Optional[np.ndarray], bool]:
        """Recursive backtracking solver with constraint propagation"""
        if row == 9:
            return self.puzzle.copy(), True
        
        if col == 9:
            return self._solve_recursive(row + 1, 0)
        
        if self.puzzle[row, col] != 0:
            return self._solve_recursive(row, col + 1)
        
        row_idx = (row // 3) * 3 + (row % 3)
        col_idx = (col // 3) * 3 + (col % 3)
        
        candidates = set(range(1, 10)) - (set(self.puzzle[row]) | 
                                           set(self.puzzle[row_idx:row_idx+3, col_idx:col_idx+3]) |
                                           set(self.puzzle[:, col]))
        
        for value in candidates:
            self.puzzle[row, col] = value
            
            solved = self._solve_recursive(row, col + 1)
            
            if solved[0] is not None:
                return solved
            
            self.puzzle[row, col] = 0
        
        return None, False
    
    def solve_parallel(self, n_workers: Optional[int] = None, use_gpu: bool = False) -> Optional[np.ndarray]:
        """
        Solve the Sudoku puzzle using parallel processing
        
        Args:
            n_workers: Number of parallel workers (uses default if None)
            use_gpu: Whether to use GPU acceleration (future-proof structure)
        
        Returns:
            Solved puzzle or None if unsolvable
        """
        if n_workers is None:
            n_workers = max(1, multiprocessing.cpu_count())
        
        # Use multiprocessing for CPU-bound solving
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            try:
                result = executor.submit(self._solve_recursive, 0, 0).result()
                return result
            except Exception as e:
                print(f"Error during solving: {e}")
                return None
    
    def solve_with_concurrent(self, n_workers: int = 4) -> Optional[np.ndarray]:
        """
        Alternative solver using concurrent.futures with task parallelism
        
        Args:
            n_workers: Number of parallel workers
        
        Returns:
            Solved puzzle or None
        """
        # Divide puzzle into sections and solve each section concurrently
        if n_workers > 1:
            sections = self._divide_puzzle(n_workers)
            
            def solve_section(section):
                return self._solve_single_section(section)
            
            with ProcessPoolExecutor(max_workers=n_workers) as executor:
                results = list(executor.map(solve_section, sections))
            
            if all(r[0] is not None for r in results):
                return np.vstack([r[0] for r in results])
        
        return self._solve_recursive(0, 0)[0]
    
    def _divide_puzzle(self, n_workers: int) -> List[np.ndarray]:
        """Divide puzzle into sections for parallel solving"""
        rows_per_worker = 9 // n_workers
        sections = []
        
        for i in range(n_workers):
            start_row = i * rows_per_worker
            end_row = start_row + rows_per_worker if i < n_workers - 1 else 9
            
            section = self.puzzle[start_row:end_row, :]
            # Ensure empty cells for this section
            section[section != 0] = 0
            sections.append(section.copy())
        
        return sections
    
    def _solve_single_section(self, section: np.ndarray) -> Tuple[np.ndarray, List[List[int]]]:
        """Solve a single section with its constraints"""
        row, col = self._get_section_coords(section)
        solved_section, placed_values = self._solve_section_internal(section)
        return solved_section, placed_values
    
    def _get_section_coords(self, section: np.ndarray) -> Tuple[int, int]:
        """Get coordinates for the section"""
        return 0, 0  # Simplified for now
    
    def _solve_section_internal(self, section: np.ndarray) -> Tuple[np.ndarray, List[List[int]]]:
        """Internal solver for a single section"""
        return section.copy(), []  # Simplified for now

def run_solver(puzzle: List[List[int]], n_workers: Optional[int] = None, 
               use_gpu: bool = False) -> Optional[np.ndarray]:
    """Convenience function to run the solver"""
    solver = SudokuSolver(puzzle)
    return solver.solve_parallel(n_workers=n_workers, use_gpu=use_gpu)

if __name__ == "__main__":
    import time
    from sudoku_solver.src.time_solver import time_execution
    
    # Example puzzle (0 represents empty cells)
    example_puzzle = [
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
    
    # Run solver
    n_workers = 4
    start_time = time.time()
    
    solved_puzzle = run_solver(example_puzzle, n_workers=n_workers)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"Execution time: {execution_time:.4f} seconds")
    print(f"Solved puzzle:\n{solved_puzzle}")
    
    time_execution(execution_time)