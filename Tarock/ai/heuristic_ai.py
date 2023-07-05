from game import *
from ai.base_ai import TarockBaseAi
import copy


class BaseHeuristicAI(TarockBaseAi):
    def get_move(self, game_state: GameState) -> Tuple[Tuple[int, int], Card]:

        # calculate all the possible moves, each move is a tuple of ((row, col), card)
        possible_moves = []
        all_cards = game_state.player_hands[game_state.get_next_player()]
        all_empty_coords = game_state.board.get_empty_coords()
        for coord in all_empty_coords:
            for card in all_cards:
                possible_moves.append((coord, card))

        # simulate each possible move and get the score
        simulation_times = 10
        scores = [0.0] * len(possible_moves)
        for i in range(len(possible_moves)):
            for j in range(simulation_times):
                temp_state = self.simulate_move(
                    possible_moves[i][0], possible_moves[i][1], game_state)
                this_score = self.evaluate_state(temp_state)
                my_score = this_score[game_state.get_next_player()]
                opponent_score = this_score[1 - game_state.get_next_player()]
                scores[i] += my_score - opponent_score
            scores[i] /= simulation_times

        # get the move with the highest score
        max_score = max(scores)
        max_score_index = scores.index(max_score)

        # return the move
        return possible_moves[max_score_index]

    def evaluate_state(self, game_state: GameState) -> Tuple[float, float]:
        raise NotImplementedError


class SimpleHeuristicAI(BaseHeuristicAI):

    def __init__(self, defense_coefficient: float = 1, attack_coefficient: float = 1, presence_coefficient: float = 5):
        self.coefficients = (defense_coefficient,
                             attack_coefficient, presence_coefficient)

    def evaluate_state(self, game_state: GameState) -> Tuple[float, float]:
        '''
        Evaluates the given game state. Returns a tuple representing the score for each player.
        '''

        # initialize scores
        scores = [0.0, 0.0]

        # score is based on linear sum of 1. total defense owned by player on the board 2. total attack of player's hand 3. total number of cards owned by player on the board
        # coefficients for each of the above is defined in the constructor
        defense_coefficient, attack_coefficient, presence_coefficient = self.coefficients

        # first look at the board to assign board-based scores
        board = game_state.board
        for row in range(3):
            for col in range(3):
                cell = board.get_cell_value((row, col))
                if cell.card is None:
                    continue
                else:
                    # cell is occupied and owned by someone
                    owner = cell.owner
                    presence_score = presence_coefficient
                    defense_score = cell.card.defense * defense_coefficient
                    scores[owner] += presence_score + defense_score

        # now look at the player's hand to assign hand-based scores
        hands = game_state.player_hands
        for player in range(2):
            hand = hands[player]
            for card in hand:
                attack_score = card.attack * attack_coefficient
                scores[player] += attack_score

        return tuple(scores)
