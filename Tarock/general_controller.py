from game import Game, Card, Board, Direction, AttackEvent, GameState
from pprint import pprint
from ALL_CARDS import ALL_CARDS
from coinflip_listener import CoinflipListenerMixin
from typing import Tuple, List, Optional
from tarock_player import TarockBasePlayer
from ai.base_ai import TarockBaseAi
from human_player import HumanTarockPlayer


class TarockGameController(CoinflipListenerMixin):

    # setup the game, player 0 is human, player 1 is AI
    def __init__(
            self,
            player1: TarockBasePlayer,
            player2: TarockBasePlayer,
    ):
        # initialize the players
        self.players = [player1, player2]



    def start_new_game(
            self,
            starting_player: int = 0,
            starting_hands: Optional[Tuple[List[Card], List[Card]]] = None,
            fair_start: bool = False
    ):
        if starting_hands is None:
            player0_hand = [Card.get_random_card(ALL_CARDS) for _ in range(5)]
            player1_hand = [Card.get_random_card(ALL_CARDS) for _ in range(5)]
            starting_hands = (player0_hand, player1_hand)
            if fair_start:
                while not self._hand_is_fair(starting_hands):
                    player0_hand = [Card.get_random_card(
                        ALL_CARDS) for _ in range(5)]
                    player1_hand = [Card.get_random_card(
                        ALL_CARDS) for _ in range(5)]
                    starting_hands = (player0_hand, player1_hand)
        self.game = Game(starting_player, starting_hands)
        self.game.register_coinflip_listener(self)

        # print the game info
        self._print_pre_game_info()

        # play the game
        final_scores = self._start_game()

        return final_scores


    def _print_pre_game_info(self):
        print("Welcome to Tarock! Starting a new game...")
        print("Player 1's hand: ")
        pprint(self.game.game_state.player_hands[0])
        print("Player 2's hand: ")
        pprint(self.game.game_state.player_hands[1])
        print(f"Starting player: {self.game.game_state.get_next_player()+1}")


    def _start_game(self):
        # play the game
        while not self.game.game_state.ended:
            # print the game state
            print("\n\nCurrent Board:")
            self._print_board(self.game.game_state.board)
            print("player 1's hand: ")
            pprint(self.game.game_state.player_hands[0])
            print("\nplayer 2's hand: ")
            pprint(self.game.game_state.player_hands[1])

            # print the next player
            next_to_play = self.game.game_state.get_next_player()
            print(f"\n\nPlayer {next_to_play+1}'s turn!")
            coord, card = self.players[next_to_play].get_move(
                self.game.game_state)
            print(
                f"Player {next_to_play+1} places {card} at ({coord[0]}, {coord[1]})")
            self.game.place_card(coord[0], coord[1], card)

        # game ended, print the final board and declare the winner
        print("\n\nFinal Board:")
        self._print_board(self.game.game_state.board)
        final_scores = self.game.game_state.get_scores()
        print("Final scores:")
        print(f"Player 1: {final_scores[0]}")
        print(f"Player 2: {final_scores[1]}")
        winner = 0 if final_scores[0] > final_scores[1] else 1
        print(f"Player {winner+1} wins!")
        return final_scores

    def _on_coinflip_result(self, attack_event: AttackEvent, favored_player: int):
        attacker = attack_event.attacker
        defender = attack_event.defender
        attacker_coords = attack_event.attacker_coords
        defender_coords = attack_event.defender_coords
        print(
            f"\nCoin flip required for {attacker.name} ({attacker_coords[0]}, {attacker_coords[1]}) attacking {defender.name} ({defender_coords[0]}, {defender_coords[1]})")
        print(f"Player {favored_player+1} wins the coin flip")

    @staticmethod
    def _hand_is_fair(starting_hands: Tuple[List[Card], List[Card]]) -> bool:
        '''
        Checks if the starting hands are fair. A fair starting hand is one where the scores of both players are within 10% of their average.
        The scores are calculated as the sum of the value of each card in the hand, where the value of each card is calculated as follows:
            - in each non-overpower direction, the card earns a value equal to its attack + defense
            - in each overpower direction, the card earns a value equal to 2 * the maximum attack/defense among all cards present, regardless of owner)
        '''
        # calculate the overpower score
        overpower_raw_score = 0
        for hand in starting_hands:
            for card in hand:
                overpower_raw_score = max(
                    card.attack, card.defense, overpower_raw_score)
        overpower_score = 2 * overpower_raw_score

        # calculate the values of each card in each direction
        scores = [0, 0]
        for i, hand in enumerate(starting_hands):
            for card in hand:
                for direction in Direction.all_directions():
                    if direction in card.directions:
                        scores[i] += overpower_score
                    else:
                        scores[i] += card.attack + card.defense

        # check if the scores are within 10% of each other
        return abs(scores[0] - scores[1]) <= 0.1 * (scores[0] + scores[1])
    
    @staticmethod
    def _print_board(board: Board):
        # generate a pretty representation of the board with 3 rows and 3 columns, each cell in 20 characters wide

        # first, generate the top border
        board_str = "┌"+"─"*20+"┬"+"─"*20+"┬"+"─"*20+"┐\n"

        # then, generate the rows
        for row in range(3):
            for i in range(5):
                board_str += "│"
                for col in range(3):
                    cell = board.cells[row][col]
                    if cell.card is None:
                        if i == 2:
                            board_str += f"({row},{col})".center(20)
                        else:
                            board_str += " "*20
                    else:
                        name_lines = cell.card.name.center(20).split('\n')
                        attack_defense = f"(🗡️ {cell.card.attack}/🛡️ {cell.card.defense})".center(
                            22)
                        attack_defense_lines = attack_defense.split('\n')
                        if i == 1:
                            board_str += name_lines[0].center(20)
                        elif i == 2:
                            board_str += attack_defense_lines[0].center(20)
                        elif i == 3:
                            direction_str = ""
                            if Direction.UP in cell.card.directions:
                                direction_str += "↑"
                            if Direction.RIGHT in cell.card.directions:
                                direction_str += "→"
                            if Direction.DOWN in cell.card.directions:
                                direction_str += "↓"
                            if Direction.LEFT in cell.card.directions:
                                direction_str += "←"
                            board_str += direction_str.center(20)
                        elif i == 4:
                            board_str += f"Player {cell.owner + 1}".center(20)
                        else:
                            board_str += " "*20
                    board_str += "│"
                board_str += "\n"
            if row != 2:
                board_str += "├"+"─"*20+"┼"+"─"*20+"┼"+"─"*20+"┤\n"

        # finally, generate the bottom border
        board_str += "└"+"─"*20+"┴"+"─"*20+"┴"+"─"*20+"┘\n"

        print(board_str)


if __name__ == "__main__":
    from ai.random_ai import RandomAI
    from ai.heuristic_ai import SimpleHeuristicAI
    # controller = TarockGameController(HumanTarockPlayer(), HumanTarockPlayer())
    # controller = TarockGameController(RandomAI(), SimpleHeuristicAI(attack_coefficient=1, defense_coefficient=1, presence_coefficient=10))
    controller = TarockGameController(SimpleHeuristicAI(attack_coefficient=1, defense_coefficient=1, presence_coefficient=1), SimpleHeuristicAI(attack_coefficient=1, defense_coefficient=1, presence_coefficient=10))

    win_counts = [0, 0]
    for _ in range(100):
        final_scores = controller.start_new_game(fair_start=True, starting_player=1)
        winner = 0 if final_scores[0] > final_scores[1] else 1
        win_counts[winner] += 1

    print(f"Player 1 won {win_counts[0]} times")
    print(f"Player 2 won {win_counts[1]} times")
