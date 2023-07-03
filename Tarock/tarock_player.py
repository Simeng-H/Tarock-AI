from game import *
from typing import Tuple

class TarockBasePlayer:
    def get_move(self, game_state: GameState) -> Tuple[Tuple[int, int], Card]:
        '''
        Provided the current game state, return a move to make, in the form of a tuple of the form:
        ((row, col), card)
        '''
        raise NotImplementedError("get_move not implemented")