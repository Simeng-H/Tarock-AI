from game import *
from tarock_player import TarockBasePlayer

class HumanTarockPlayer(TarockBasePlayer):
    def get_move(self, game_state: GameState) -> Tuple[Tuple[int, int], Card]:
        '''
        Provided the current game state, return a move to make, in the form of a tuple of the form:
        ((row, col), card)
        '''
        # prompt the player to select a card for placement
        print("Select a card to place on the board: [1-5]")
        for i, card in enumerate(game_state.player_hands[game_state.get_next_player()]):
            print(f"{i+1}: {card}")
        card_index = int(input()) - 1
        card = game_state.player_hands[game_state.get_next_player()][card_index]

        # prompt the player to select a cell to place the card in
        print("\nSelect a cell to place the card in: [1-9, upper left to lower right, row by row]")
        placement_index = int(input()) - 1
        row = placement_index // 3
        col = placement_index % 3

        # return the move
        return (row, col), card