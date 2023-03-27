import numpy as np
from typing import List, Tuple
from termcolor import colored
import random
import sys


class Sudoku:

    def __init__(self, board = None) -> None:
        if board is None:
            self.board: np.ndarray = np.zeros((9, 9), dtype=int)
        else:
            assert type(board) == np.ndarray
            assert board.shape == (9, 9)
            self.board: np.array = board
        self.given_numbers_indices = np.nonzero(self.board)
        self.given_numbers_indices = tuple(zip(self.given_numbers_indices[0], self.given_numbers_indices[1]))
    
    def __repr__(self) -> str:
        s: str = '╔═══╤═══╤═══╦═══╤═══╤═══╦═══╤═══╤═══╗\n'
        for i, row in enumerate(self.board):
            for j, number in enumerate(row):
                if j % 3 == 0:
                    s += '║'
                else:
                    s += '|'
                if number == 0:
                    s += '   '
                else:
                    if (i, j) in self.given_numbers_indices:
                        s += ' ' + colored(str(number), 'red') + ' '
                    else:
                        s += ' ' + str(number) + ' '
            if i != 8:
                if (i + 1) % 3 == 0:
                    s += '║\n╠═══╪═══╪═══╬═══╪═══╪═══╬═══╪═══╪═══╣\n'
                else:
                    s += '║\n╟───┼───┼───╫───┼───┼───╫───┼───┼───╢\n'

        s += '║\n╚═══╧═══╧═══╩═══╧═══╧═══╩═══╧═══╧═══╝'
            
        return s

    def write(self, number: int, row: int, column: int) -> bool:
        '''Returns True when the number was succesfully written.'''

        if self._is_move_legal(number, row, column):
            self.board[row][column] = number
            return True
        else:
            return False

    def _is_move_legal(self, number: int, row: int, column: int) -> bool:
        if (row, column) in self.given_numbers_indices:
            return False
        if number == 0:
            return True
        if number > 9:
            return False
        
        board_copy: np.ndarray = self.board.copy()
        board_copy[row][column] = number # Trying the test number on a copy of the board
        region: np.ndarray = self._get_region(row, column).copy()
        region[row % 3][column % 3] = number # Inserting the test number into the region

        if np.count_nonzero(board_copy[row] == number) > 1:
            return False
        if np.count_nonzero(board_copy[:, column] == number) > 1:
            return False
        if np.count_nonzero(region == number) > 1:
            return False
        return True

    def _get_region(self, row: int, column: int) -> np.ndarray:
        region_row = row - row % 3
        region_column = column - column % 3
        return self.board[region_row:region_row+3, region_column:region_column+3]
    
    def is_solved(self) -> bool:
        if 0 in self.board:
            return False
        return True


class SudokuMaker:

    def create_random_sudoku(self, hints: int = 17, sudoku_type: str = 'standard') -> Sudoku:
        '''Creates a random sudoku by:
        - Creating a board with 8 different random numbers at random positions
        - Solving the sudoku
        - Removing random numbers, so that "hints" numbers are left
        
        Types: "standard", "diagonal"'''

        board = self._create_board()

        if sudoku_type == "standard":
            sudoku = Sudoku(board)
        elif sudoku_type == "diagonal":
            sudoku = DiagonalSudoku(board)
        else:
            raise ValueError(f"{sudoku_type} is not a supported sudoku type.")

        sudoku_solver = SudokuSolverBruteforce()
        sudoku_solver.solve(sudoku)
        self._remove_numbers(sudoku, hints)
        sudoku = type(sudoku)(sudoku.board)
        return sudoku

    def _remove_numbers(self, sudoku: Sudoku, hints: int) -> None:
        numbers_to_remove = 81 - hints
        while numbers_to_remove != 0:
            row = random.randint(0, 8)
            column = random.randint(0, 8)
            if sudoku.board[row][column] != 0:
                if sudoku.write(0, row, column):
                    numbers_to_remove -= 1

    def _create_board(self) -> np.ndarray:
        board: np.ndarray = np.zeros((9, 9), dtype=int)
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        numbers.pop(-1)
        
        while len(numbers) > 0:
            row = random.randint(0, 8)
            column = random.randint(0, 8)
            if board[row][column] == 0:
                board[row][column] = numbers[0]
                numbers.pop(0)

        return board
        

class SudokuSolverBruteforce:

    def solve(self, sudoku: Sudoku, use_recursion: bool = False) -> None:
        '''Solves a sudoku using a bruteforce algorithm.'''

        if not sudoku.is_solved():
            start_row, start_column = self._get_start_row_column(sudoku)
            if use_recursion: # Not recommended
                sys.setrecursionlimit(10000)
                self._solve_recursive(sudoku, 1, start_row, start_column)
            else:
                self._solve_iterative(sudoku, start_row, start_column)

    def _solve_recursive(self, sudoku: Sudoku, start_number: int = 1, row: int = 0, column: int = 0) -> None:
        if sudoku.write(start_number, row, column):
            if not sudoku.is_solved():
                new_row, new_column = self._next_row_column(sudoku, row, column, 1)
                self._solve_recursive(sudoku, sudoku.board[new_row][new_column] + 1, new_row, new_column)
        else:
            if start_number <= 8:
                self._solve_recursive(sudoku, start_number + 1, row, column)
            else: # Backtracking
                sudoku.write(0, row, column) # Deleting the written wrong number
                new_row, new_column = self._next_row_column(sudoku, row, column, -1)
                self._solve_recursive(sudoku, sudoku.board[new_row][new_column] + 1, new_row, new_column)

    def _solve_iterative(self, sudoku: Sudoku, row: int = 0, column: int = 0) -> None: 
        number: int = 1
        while not sudoku.is_solved():
            if sudoku.write(number, row, column):
                row, column = self._next_row_column(sudoku, row, column, 1)
                number = 1
            elif number < 9:
                number += 1
            else:
                sudoku.write(0, row, column)
                row, column = self._next_row_column(sudoku, row, column, -1)
                number = sudoku.board[row][column] + 1           

    def _next_row_column(self, sudoku: Sudoku, row: int, column: int, direction: int) -> Tuple[int, int]:
        sudoku_size: int = len(sudoku.board)

        if direction == 1:
            new_row: int = row + ((column + 1) // sudoku_size)
            new_column: int = (column + 1) % sudoku_size
        elif direction == -1:
            if column == 0:
                new_row: int = row - 1
                new_column: int = 8
            else:
                new_row: int = row
                new_column: int = column - 1

        if (new_row, new_column) in sudoku.given_numbers_indices:
            new_row, new_column = self._next_row_column(sudoku, new_row, new_column, direction)

        return new_row, new_column

    def _get_start_row_column(self, sudoku: Sudoku) -> Tuple[int, int]:
        row: int = 0
        column: int = 0
        while sudoku.board[row][column] != 0:
            row, column = self._next_row_column(sudoku, row, column, 1)
        return row, column


class DiagonalSudoku(Sudoku):

    def _is_move_legal(self, number: int, row: int, column: int) -> bool:
        if (row, column) in self.given_numbers_indices:
            return False
        if number == 0:
            return True
        if number > 9:
            return False
        
        board_copy: np.ndarray = self.board.copy()
        board_copy[row][column] = number # Trying the test number on a copy of the board
        region: np.ndarray = self._get_region(row, column).copy()
        region[row % 3][column % 3] = number # Inserting the test number into the region

        if np.count_nonzero(board_copy[row] == number) > 1:
            return False
        if np.count_nonzero(board_copy[:, column] == number) > 1:
            return False
        if np.count_nonzero(region == number) > 1:
            return False
        if np.count_nonzero(np.diagonal(board_copy) == number) > 1:
            return False
        if np.count_nonzero(np.diagonal(np.flipud(board_copy)) == number) > 1:
            return False
        return True


if __name__ == '__main__':
    difficult_board = np.array([[1, 2, 0, 4, 0, 0, 3, 0, 0],
                                [3, 0, 0, 0, 1, 0, 0, 5, 0],
                                [0, 0, 6, 0, 0, 0, 1, 0, 0],
                                [7, 0, 0, 0, 9, 0, 0, 0, 0],
                                [0, 4, 0, 6, 0, 3, 0, 0, 0],
                                [0, 0, 3, 0, 0, 2, 0, 0, 0],
                                [5, 0, 0, 0, 8, 0, 7, 0, 0],
                                [0, 0, 7, 0, 0, 0, 0, 0, 5],
                                [0, 0, 0, 0, 0, 0, 0, 9, 8]])

    sudoku_maker = SudokuMaker()
    sudo = sudoku_maker.create_random_sudoku(sudoku_type="standard")
    print(sudo)
    ssolver = SudokuSolverBruteforce()
    ssolver.solve(sudo)
    print(sudo)