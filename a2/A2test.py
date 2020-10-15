#A2 Test Cases
#fixtures
from typing import List, Optional, Tuple
import os
import pygame
import pytest

from block import Block
from blocky import _block_to_squares
from goal import BlobGoal, PerimeterGoal, _flatten, generate_goals
from player import _get_block
from renderer import Renderer
from settings import COLOUR_LIST

@pytest.fixture
def board_1x1() -> Block:
    return Block((0,0), 750, COLOUR_LIST[1], 0, 0)

@pytest.fixture
def board_2x2() -> Block:
    return Block((0,0), 750, COLOUR_LIST[2], 0, 1)

@pytest.fixture
def flattened_board_1x1() -> List[List[Tuple[int, int, int]]]:
    return [[COLOUR_LIST[1]]]

@pytest.fixture
def flattened_board_2x2() -> List[List[Tuple[int, int, int]]]:
    return [[COLOUR_LIST[2], COLOUR_LIST[2]], [COLOUR_LIST[2], COLOUR_LIST[2]]]


@pytest.fixture
def renderer() -> Renderer:
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    return Renderer(750)


@pytest.fixture
def child_block() -> Block:
    """Create a reference child block with a size of 750 and a max_depth of 0.
    """
    return Block((0, 0), 750, COLOUR_LIST[0], 0, 0)


@pytest.fixture
def board_16x16() -> Block:
    """Create a reference board with a size of 750 and a max_depth of 2.
    """
    # Level 0
    board = Block((0, 0), 750, None, 0, 2)

    # Level 1
    colours = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board, colours)

    # Level 2
    colours = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board.children[0], colours)

    return board

def set_children(block: Block, colours: List[Optional[Tuple[int, int, int]]]) \
        -> None:
    """Set the children at <level> for <block> using the given <colours>.

    Precondition:
        - len(colours) == 4
        - block.level + 1 <= block.max_depth
    """
    size = block._child_size()
    positions = block._children_positions()
    level = block.level + 1
    depth = block.max_depth

    block.children = []  # Potentially discard children
    for i in range(4):
        b = Block(positions[i], size, colours[i], level, depth)
        block.children.append(b)


#Goal test cases
def test_generate_goals() -> None:
    lst0 = generate_goals(0)
    lst1 = generate_goals(1)
    lst2 = generate_goals(2)
    lst3 = generate_goals(3)
    lst4 = generate_goals(4)
    temp_list = []

    assert all(isinstance(item, PerimeterGoal) for item in lst0) or all(isinstance(item, BlobGoal) for item in lst0)
    for item in lst0:
        assert item.colour not in temp_list
        temp_list.append(item.colour)
    assert all(isinstance(item, PerimeterGoal) for item in lst1) or all(isinstance(item, BlobGoal) for item in lst1)
    temp_list = []
    for item in lst1:
        assert item.colour not in temp_list
        temp_list.append(item.colour)
    assert all(isinstance(item, PerimeterGoal) for item in lst2) or all(isinstance(item, BlobGoal) for item in lst2)
    temp_list = []
    for item in lst2:
        assert item.colour not in temp_list
        temp_list.append(item.colour)
    assert all(isinstance(item, PerimeterGoal) for item in lst3) or all(isinstance(item, BlobGoal) for item in lst3)
    temp_list = []
    for item in lst3:
        assert item.colour not in temp_list
        temp_list.append(item.colour)
    assert all(isinstance(item, PerimeterGoal) for item in lst4) or all(isinstance(item, BlobGoal) for item in lst4)
    temp_list = []
    for item in lst4:
        assert item.colour not in temp_list
        temp_list.append(item.colour)


def test_flatten(board_1x1, board_2x2, flattened_board_1x1, flattened_board_2x2) -> None:
    result = _flatten(board_1x1)
    result2 = _flatten(board_2x2)
    for sublist in result:
        assert len(result) == len(sublist)
    assert result == flattened_board_1x1
    for sublist in result2:
        assert len(result2) == len(sublist)
    assert result2 == flattened_board_2x2

def test_perimeter(board_1x1, board_2x2) -> None:
    correct_scores = [
        (COLOUR_LIST[0], 0),
        (COLOUR_LIST[1], 4),
        (COLOUR_LIST[2], 0),
        (COLOUR_LIST[3], 0)
    ]
    for colour, expected in correct_scores:
        goal = PerimeterGoal(colour)
        assert goal.score(board_1x1) == expected

    correct_scores2 = [
        (COLOUR_LIST[0], 0),
        (COLOUR_LIST[1], 0),
        (COLOUR_LIST[2], 8),
        (COLOUR_LIST[3], 0)
    ]

    for colour, expected in correct_scores2:
        goal = PerimeterGoal(colour)
        assert goal.score(board_2x2) == expected


def test_blob(board_1x1, board_2x2) -> None:
    correct_scores = [
        (COLOUR_LIST[0], 0),
        (COLOUR_LIST[1], 1),
        (COLOUR_LIST[2], 0),
        (COLOUR_LIST[3], 0)
    ]
    for colour, expected in correct_scores:
        goal = BlobGoal(colour)
        assert goal.score(board_1x1) == expected

    correct_scores2 = [
        (COLOUR_LIST[0], 0),
        (COLOUR_LIST[1], 0),
        (COLOUR_LIST[2], 4),
        (COLOUR_LIST[3], 0)
    ]
    for colour, expected in correct_scores2:
        goal = BlobGoal(colour)
        assert goal.score(board_2x2) == expected


def test_undiscovered_blob_size(board_16x16) -> None:
    goal = BlobGoal(COLOUR_LIST[1])
    flattened = _flatten(board_16x16)
    visited = [
        [0, 0, 1, 1],
        [0, 0, 1, 1],
        [1, -1, 0, 0],
        [0, 0, 0, 0]
    ]
    assert goal._undiscovered_blob_size((2, 1), flattened, visited) == 1
    visited = [
        [0, 0, 1, 1],
        [0, 0, 1, 1],
        [1, -1, 0, 0],
        [0, 0, 0, 0]
    ]
    assert goal._undiscovered_blob_size((2,0), flattened, visited) == 0
    visited = [
        [0, 0, 1, -1],
        [0, 0, -1, 1],
        [-1, -1, 0, 0],
        [0, 0, 0, 0]
    ]
    assert goal._undiscovered_blob_size((0, 3), flattened, visited) == 1


def test_block_to_squares(board_2x2) -> None:
    squares = set(_block_to_squares(board_2x2))
    expected = {(COLOUR_LIST[2],(0,0),750)}
    assert squares == expected


#Block Test cases
def test_block_smash(board_1x1, board_2x2, board_16x16) -> None:
    board_1x1.smash()
    assert len(board_1x1.children) == 0
    assert board_1x1.colour == COLOUR_LIST[1]
    board_2x2.smash()
    assert len(board_2x2.children) == 4
    assert board_2x2.colour is None
    for child in board_2x2.children:
        assert len(child.children) == 0
        assert child.colour in COLOUR_LIST
    child.smash()
    assert len(child.children) == 0
    assert child.colour in COLOUR_LIST

    block = board_16x16.children[2]
    block.smash()
    assert len(block.children) == 4
    assert block.colour is None
    for child in block.children:
        assert len(child.children) == 0
        assert child.colour in COLOUR_LIST

    block2 = board_16x16.children[0]
    block2.smash()
    assert len(block2.children) == 4
    assert block2.colour is None
    for child in block2.children:
        assert len(child.children) == 0
        assert child.colour in COLOUR_LIST

    board_16x16.smash()
    assert len(board_16x16.children) == 4
    assert board_16x16.colour is None
    assert len(board_16x16.children[1].children) == 0
    assert len(board_16x16.children[3].children) == 0



if __name__ == '__main__':
    pytest.main(['A2test.py'])


