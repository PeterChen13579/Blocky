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
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple, Union
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    lst = []
    goals = generate_goals(num_human + num_random + len(smart_players))
    for i in range(num_human):
        a = HumanPlayer(i, goals[i])
        lst.append(a)
    for w in range(num_random):
        b = RandomPlayer(w+num_human, goals[w+num_human])
        lst.append(b)
    for z in range(len(smart_players)):
        c = SmartPlayer(num_human + num_random + z,
                        goals[z+num_human+num_random], smart_players[z])
        lst.append(c)
    return lst


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    if len(block.children) == 0 and level >= block.level or \
            len(block.children) == 4 and level == block.level:
        if block.position[0] <= location[0] < block.position[0] + block.size \
                and block.position[1] <= location[1] < block.position[1] + \
                block.size:
            return block
        else:
            return None
    else:
        for i in range(0, 4):
            if _get_block(block.children[i], location, level) is not None:
                return _get_block(block.children[i], location, level)
        return None


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player."""
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event."""
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    """ Creates the move"""
    return action[0], action[1], block


def _generate_random_valid_move(board: Block, location: Tuple[int, int],
                                level: int, colour: Tuple[int, int, int]) \
        -> Union[bool, Tuple[str, Optional[int]]]:
    """Generates a random move(swap, paint, combine, smash, rotate)
    If it does not work on given board, location and level, return False,
    otherwise, returns True.
    """
    move = 0
    valid_move = False
    rand_block_1 = _get_block(board, location, level)
    rand_move = random.randint(0, 6)
    # TO TA OR PROFESSOR:
    # WHY DOES THE "IF" RUNS THE ACTION????????????????????????????
    if rand_move == 0:
        if rand_block_1.swap(1):
            valid_move = True
            move = SWAP_VERTICAL
    if rand_move == 1:
        if rand_block_1.swap(0):
            valid_move = True
            move = SWAP_HORIZONTAL
    if rand_move == 2:
        if rand_block_1.rotate(1):
            valid_move = True
            move = ROTATE_CLOCKWISE
    if rand_move == 3:
        if rand_block_1.rotate(3):
            valid_move = True
            move = ROTATE_COUNTER_CLOCKWISE
    if rand_move == 4:
        if rand_block_1.smashable():
            rand_block_1.smash()
            valid_move = True
            move = SMASH
    if rand_move == 5:
        if rand_block_1.paint(colour):
            valid_move = True
            move = PAINT
    if rand_move == 6:
        if rand_block_1.combine():
            valid_move = True
            move = COMBINE
    if not valid_move:
        return False
    else:
        return move


class HumanPlayer(Player):
    """A human player.
     """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, min(self._level, board.max_depth))
        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)
            self._desired_action = None
            return move


class RandomPlayer(Player):
    """A computer player that randomly generates moves until it is a correct
    move and plays that move onto the board.
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    # _level:
    #   The level of the Block that the user selected most recently.
    _proceed: bool
    _level: int

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize a random player with a given player_id and goal"""
        super().__init__(player_id, goal)
        self._level = 0
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Returns the block selected"""
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the mouse click by proceeding"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None   # Do not change
        rand_block_2 = None
        valid_move = False
        while valid_move is False:
            a = board.create_copy()
            level = random.randint(0, board.max_depth)
            location = (random.randint(0, board.size-1),
                        random.randint(0, board.size-1))
            rand_block_2 = _get_block(board, location, level)
            valid_move = _generate_random_valid_move \
                (a, location, level, self.goal.colour)
        move = _create_move(valid_move, rand_block_2)
        self._proceed = False  # Must set to False before returning!
        return move


class SmartPlayer(Player):
    """A smart computer player where they randomly generate a number of
    moves and decides the best moves to plays.
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    # _level:
    #    The level of the Block that the user selected most recently.
    # _difficulty:
    #   The difficulty it is to play against the smart player
    _proceed: bool
    _level: int
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        """Initialize a smart player with given player_id, goal and difficulty
        """
        super().__init__(player_id, goal)
        self._level = 0
        self._proceed = False
        self._difficulty = difficulty

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the selected block for the move"""
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to relevant event when mouse is clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        lst = []
        score = []
        rand = 0
        curr_score = self.goal.score(board)
        a = board.create_copy()

        for _ in range(self._difficulty):
            move = False
            while move is False:
                a = board.create_copy()
                level = random.randint(0, board.max_depth)
                location = (random.randint(0, board.size-1),
                            random.randint(0, board.size-1))
                move = _generate_random_valid_move \
                    (a, location, level, self.goal.colour)
                rand = _get_block(board, location, level)
            score.append(self.goal.score(a))
            lst.append(_create_move(move, rand))
        if max(score) <= curr_score:
            self._proceed = False  # Must set to False before returning!
            return _create_move(PASS, board)
        else:
            num = score.index(max(score))
            self._proceed = False  # Must set to False before returning!
            return lst[num]


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
