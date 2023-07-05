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

        # First, check if the game is over, if so, assign 100 points to the winner
        if game_state.is_terminal():
            final_game_scores = game_state.get_scores()
            winner = final_game_scores.index(max(final_game_scores))
            scores = [0.0, 0.0]
            scores[winner] = 100.0
            return tuple(scores)

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


class AdvancedHeuristicAI(BaseHeuristicAI):

    def __init__(self, defense_coefficient: float = 1, attack_coefficient: float = 1, presence_coefficient: float = 5):
        self.coefficients = (defense_coefficient,
                             attack_coefficient,
                             presence_coefficient
                             )

    def evaluate_state(self, game_state: GameState) -> Tuple[float, float]:
        '''
        Evaluates the given game state. Returns a tuple representing the score for each player.
        '''

        # First, check if the game is over, if so, assign 100 points to the winner
        if game_state.is_terminal():
            final_game_scores = game_state.get_scores()
            winner = final_game_scores.index(max(final_game_scores))
            scores = [0.0, 0.0]
            scores[winner] = 100.0
            return tuple(scores)
        
        # initialize scores
        scores = [0.0, 0.0]

        # score is based on average exposed defense, average remaining attack, and total number of cards owned by player on the board

        # retrieve the coefficients
        defense_coefficient, attack_coefficient, presence_coefficient = self.coefficients

        # Each card has an exposed edge in a direction if the adjacent cell in that direction is empty.
        # The defense for an edge is, if the edge is not overpower, the defense of the card in that direction, otherwise, the maximum attack of all cards yet to be played.
        # determine the maximum attack of all cards yet to be played
        attacks = [
            [card.attack for card in game_state.player_hands[0]],
            [card.attack for card in game_state.player_hands[1]]
        ]
        max_attack = max(max(attacks[0]), max(attacks[1]))
        overpower_defense_score = max_attack

        # first look at the board to assign board-based defense scores
        board = game_state.board
        exposed_defenses = [[],[]]
        presence_raw_scores = [0.0, 0.0]
        for row in range(3):
            for col in range(3):
                this_cell = board.get_cell_value((row, col))
                
                # skip empty cells
                if this_cell.card is None:
                    continue

                owner = this_cell.owner
                card = this_cell.card
                defense = card.defense
                overpower_directions = card.directions

                # add the presence score
                presence_raw_scores[owner] += 1.0

                for direction in Direction.all_directions():
                    try:
                        adj_coord = board.get_adj_coord_in_direction(coord=(row, col), direction=direction)
                    except ValueError:
                        continue

                    # skip if the adjacent cell is not empty
                    if not board.get_cell_owner(adj_coord) == None:
                        continue

                    # check if the edge is overpower
                    if direction in overpower_directions:
                        this_edge_score = overpower_defense_score
                    else:
                        this_edge_score = defense

                    # add the edge score to the exposed defense score
                    exposed_defenses[owner].append(this_edge_score)

        # calculate the average exposed defense, for player with no exposed edges, set the average to the maximum attack (i.e. unbreakable)
        defense_raw_scores = [0.0, 0.0]
        for i in range(2):
            if len(exposed_defenses[i]) == 0:
                defense_raw_scores[i] = max_attack
            else:
                defense_raw_scores[i] = sum(exposed_defenses[i]) / len(exposed_defenses[i])

        # now look at the player's hand to assign hand-based attack scores. A card's attack score is its attack if no overpower, otherwise the average across all directions
        # the attack score in a overpower direction in the maximum defense among all cards yet to be played and exposed edges on the board
        maximum_defense_candidates = [
            max(exposed_defenses[0] or [0]),
            max(exposed_defenses[1] or [0]),
            max(([card.defense for card in game_state.player_hands[0]]) or [0]),
            max(([card.defense for card in game_state.player_hands[1]]) or [0])
        ]
        maximum_defense = max(maximum_defense_candidates)

        # calculate the attack scores for both players
        hands = game_state.player_hands
        remaining_attacks = [[],[]]
        for player in range(2):
            hand = hands[player]
            for card in hand:
                attack = card.attack
                overpower_directions = card.directions
                if len(overpower_directions) == 0:
                    card_attack_score = attack
                else:
                    card_attack_score = (maximum_defense * len(overpower_directions) + attack * (4 - len(overpower_directions)) ) / 4
                remaining_attacks[player].append(card_attack_score)

        # calculate the average remaining attack
        attack_raw_scores = [
            sum(remaining_attacks[0]) / (len(remaining_attacks[0]) or 1),
            sum(remaining_attacks[1]) / (len(remaining_attacks[1]) or 1)
        ]

        fianl_scores = [
            defense_raw_scores[0] * defense_coefficient + attack_raw_scores[0] * attack_coefficient + presence_raw_scores[0] * presence_coefficient,
            defense_raw_scores[1] * defense_coefficient + attack_raw_scores[1] * attack_coefficient + presence_raw_scores[1] * presence_coefficient
        ]

        return tuple(fianl_scores)

                    
                    
                

