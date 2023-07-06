from game import *
from ai.base_ai import TarockBaseAi

class RandomAI(TarockBaseAi):
    def get_move(self, game_state: GameState) -> Tuple[Tuple[int, int], Card]:
        # get a random card from the hand
        card = random.choice(game_state.player_hands[game_state.get_next_player()])

        # get all unoccupied cells from the board
        unoccupied_cell_coords = []
        for row in range(3):
            for col in range(3):
                cell = game_state.board.get_cell_value((row, col))
                if cell.card is None:
                    unoccupied_cell_coords.append((row, col))

        # get a random unoccupied cell
        row, col = random.choice(unoccupied_cell_coords)

        # return the move
        return (row, col), card