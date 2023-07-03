from game import Game, Card, Board, Direction, AttackEvent, GameState
from pprint import pprint
from ALL_CARDS import ALL_CARDS
from coinflip_listener import CoinflipListenerMixin
from typing import Tuple
from ai.base_ai import TarockBaseAi

class SemiInteractiveTarockController(CoinflipListenerMixin):

    # setup the game, player 0 is human, player 1 is AI
    def __init__(self, ai: TarockBaseAi, player_start: bool = True):
        player0_hand = [Card.get_random_card(ALL_CARDS) for _ in range(5)]
        player1_hand = [Card.get_random_card(ALL_CARDS) for _ in range(5)]
        starting_hands = [player0_hand, player1_hand]
        starting_player = 0 if player_start else 1
        self.game = Game(starting_player, starting_hands)
        self.game.register_coinflip_listener(self)
        self.ai = ai
        self.PLAYER = 0
        self.AI = 1

    def start_game(self):
        # print the game info
        print("Welcome to Tarock! Starting a new game...")
        print("\nPlayer 1's hand: ")
        pprint(self.game.game_state.player_hands[0])
        print("\nPlayer 2's hand: ")
        pprint(self.game.game_state.player_hands[1])
        print(f"\nStarting player: {self.game.game_state.get_next_player()+1}")

        # # play the game
        while not self.game.game_state.ended:
            # print the game state
            print("\n\nCurrent Board:")
            self._print_board(self.game.game_state.board)
            print("player 1's hand: ")
            pprint(self.game.game_state.player_hands[0])
            print("\nplayer 2's hand: ")
            pprint(self.game.game_state.player_hands[1])

            # different logic for human and AI
            player_turn = self.game.game_state.get_next_player() == self.PLAYER

            if player_turn:
                print("\n\nPlayer's turn!")
                # prompt the player to select a card for placement
                print("Select a card to place on the board: [1-5]")
                for i, card in enumerate(self.game.game_state.player_hands[self.game.game_state.get_next_player()]):
                    print(f"{i+1}: {card}")
                card_index = int(input()) - 1
                card = self.game.game_state.player_hands[self.game.game_state.get_next_player()][card_index]

                # prompt the player to select a cell to place the card in
                print("\nSelect a cell to place the card in: [1-9, upper left to lower right, row by row]")
                placement_index = int(input()) - 1
                row = placement_index // 3
                col = placement_index % 3

                # place the card
                self.game.place_card(row, col, card)

            # AI's logic
            else:
                print("\n\nAI's turn!")
                coord, card = self.ai.get_move(self.game.game_state)
                print(f"AI places {card} at ({coord[0]}, {coord[1]})")
                self.game.place_card(coord[0], coord[1], card)

        # game ended, print the final board and declare the winner
        print("\n\nFinal Board:")
        self._print_board(self.game.game_state.board)
        final_scores = self.game.game_state.get_scores()
        print(f"\nPlayer's score: {final_scores[0]}")
        print(f"AI's score: {final_scores[1]}")
        if final_scores[0] > final_scores[1]:
            print("Player wins!")
        elif final_scores[0] < final_scores[1]:
            print("AI wins!")

    def on_coinflip_result(self, attack_event: AttackEvent, favored_player: int):
        attacker = attack_event.attacker
        defender = attack_event.defender
        attacker_coords = attack_event.attacker_coords
        defender_coords = attack_event.defender_coords
        print(f"\nCoin flip required for {attacker.name} ({attacker_coords[0]}, {attacker_coords[1]}) attacking {defender.name} ({defender_coords[0]}, {defender_coords[1]})")
        if favored_player == self.PLAYER:
            print("Player wins the coinflip!")
        else:
            print("AI wins the coinflip!")

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
                        attack_defense = f"(🗡️ {cell.card.attack}/🛡️ {cell.card.defense})".center(22)
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
    controller = SemiInteractiveTarockController(RandomAI())
    controller.start_game()