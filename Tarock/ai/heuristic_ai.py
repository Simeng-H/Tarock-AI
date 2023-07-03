from game import *
from ai.base_ai import TarockAI
import copy

class SimpleHeuristicAI(TarockAI):
    # TODO: pass various parameters into the constructor to control the behavior of the AI
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
                temp_state = SimpleHeuristicAI.simulate_move(possible_moves[i][0], possible_moves[i][1], game_state)
                scores[i] += SimpleHeuristicAI.evaluate_state(temp_state)[game_state.get_next_player()]
            scores[i] /= simulation_times

        # get the move with the highest score
        max_score = max(scores)
        max_score_index = scores.index(max_score)

        # return the move
        return possible_moves[max_score_index]

    @staticmethod
    def evaluate_state(game_state: GameState) -> Tuple[float, float]:
        '''
        Evaluates the given game state. Returns a tuple representing the score for each player.
        '''

        # initialize scores
        scores = [0.0, 0.0]

        # score is based on linear sum of 1. total defense owned by player on the board 2. total attack of player's hand 3. total number of cards owned by player on the board
        # coefficients for each of the above
        defense_coefficient = 1
        attack_coefficient = 1
        presence_coefficient = 1.5

        # first look at the board to assign board-based scores
        board = game_state.board
        for row in range(3):
            for col in range(3):
                cell = board.get_cell_value((row, col))
                if cell.card is None:
                    continue
                else:
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


        