"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import math
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    # determines if Perimeter Goal or Blob Goal
    num = random.randint(0, 1)
    # lst keeps track goals, track_colour keeps track colour
    lst, track_colour = [], []
    if num == 0:
        # Adds to lst of BlobGoal until it reaches num_goals number of goals
        while num_goals > 0:
            num = random.randint(0, 3)
            if num not in track_colour:
                track_colour.append(num)
                lst.append(BlobGoal(COLOUR_LIST[num]))
                num_goals -= 1
    else:
        # Adds to lst of PerimeterGoal until it reaches num_goals number of
        # goals
        while num_goals > 0:
            num = random.randint(0, 3)
            if num not in track_colour:
                track_colour.append(num)
                lst.append(PerimeterGoal(COLOUR_LIST[num]))
                num_goals -= 1
    return lst


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    if block.level == block.max_depth:
        return [[block.colour]]
    elif len(block.children) == 0:
        temp = []
        unit = int(math.pow(2, (block.max_depth - block.level)))
        for i in range(unit):
            temp.append([block.colour] * unit)
        return temp
    else:
        temp = []
        top_left = _flatten(block.children[1])
        bottom_left = _flatten(block.children[2])
        top_right = _flatten(block.children[0])
        bottom_right = _flatten(block.children[3])
        for i in range(len(top_left)):
            tup = top_left[i] + bottom_left[i]
            temp.append(tup)
        for i in range(len(top_right)):
            tup = top_right[i] + bottom_right[i]
            temp.append(tup)

    return temp


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour."""
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal."""
        raise NotImplementedError


class PerimeterGoal(Goal):
    """Stores the score for players. This goal is for storing scores of
    player colours around the perimeter of the box"""

    def score(self, board: Block) -> int:
        """Calculates the score for perimeter goal"""
        flattened = _flatten(board)
        score = 0
        length = len(flattened)
        for i in range(length):
            if flattened[i][0] == self.colour:
                score += 1
            if flattened[i][-1] == self.colour:
                score += 1
            if flattened[0][i] == self.colour:
                score += 1
            if flattened[-1][i] == self.colour:
                score += 1
        return score

    def description(self) -> str:
        """Returns a description for perimeter goal"""
        return 'Player gains a point for each ' + colour_name(self.colour) + \
               ' connected along the perimeter'


class BlobGoal(Goal):
    """Stores the goal for players. Blob goal accounts for the max score for
    player's colours connected top/left/right/bottom together. Player gains
    a point for each block connected together."""

    def score(self, board: Block) -> int:
        """Calculates the score for blob goal"""
        score = []
        flatten_board = _flatten(board)
        board_size = len(flatten_board)
        # fill the board with -1's
        visit = [[-1] * board_size for _ in range(board_size)]

        for i in range(board_size):
            for w in range(board_size):
                if visit[i][w] == -1:
                    score.append \
                        (self._undiscovered_blob_size
                         ((i, w), flatten_board, visit))
        return max(score)

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        if len(board) > pos[0] >= 0 and len(board) > pos[1] >= 0 and \
                visited[pos[0]][pos[1]] == -1:
            # if it is that colour
            if board[pos[0]][pos[1]] == self.colour:
                visited[pos[0]][pos[1]] = 1
                size = 1
                # 2 for loops checks left, top, right, bottom
                for i in range(-1, 2):
                    size += self._undiscovered_blob_size \
                        ((i + pos[0], pos[1]), board, visited)
                for w in range(-1, 2):
                    size += self._undiscovered_blob_size \
                        ((pos[0], w + pos[1]), board, visited)
                return size
            else:
                visited[pos[0]][pos[1]] = 0
        return 0

    def description(self) -> str:
        """Returns a description for blob goal"""
        return 'Player gains a point for each ' + colour_name(self.colour) + \
               ' connected together'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
