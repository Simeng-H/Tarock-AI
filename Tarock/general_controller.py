from game_event_listener import *
from game import Game, Card, Board, Direction, AttackEvent, GameState
from pprint import pprint
from ALL_CARDS import ALL_CARDS
from coinflip_listener import CoinflipListenerMixin
from typing import Tuple, List, Optional
from tarock_player import TarockBasePlayer
from ai.base_ai import TarockBaseAi
from human_player import HumanTarockPlayer
from tqdm import trange


class TarockGameController(CoinflipListenerMixin):

    # setup the game, player 0 is human, player 1 is AI
    def __init__(
            self,
            player1: TarockBasePlayer,
            player2: TarockBasePlayer,
    ):
        # initialize the players
        self.players = [player1, player2]
        self.game_event_listeners: List[BaseGameEventListener] = []
        self.player_game_event_listeners: List[Optional[BaseGameEventListener]] = [None, None]

    # TODO: make this automatic
    def register_event_listener(self, listener: BaseGameEventListener, player_index: int = -1):
        self.game_event_listeners.append(listener)

        # TODO: safety check, maybe?
        if player_index >= 0:
            self.player_game_event_listeners[player_index] = listener

    def dispatch_event(self, event: GameEvent, players_only = False, players_to_notify: List[int] = []):
        if players_only:
            for player_index in players_to_notify:
                listener = self.player_game_event_listeners[player_index]
                if listener is not None:
                    listener._on_game_event(event)
        else:
            for listener in self.game_event_listeners:
                listener._on_game_event(event)
        

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

        # initialize the game
        self.game = Game(starting_player, starting_hands)
        self.game.register_coinflip_listener(self)
        self.dispatch_event(GameStartEvent(self.game.game_state))

        # play the game
        final_scores = self._start_game()

        return final_scores

    def _start_game(self):
        # play the game
        while not self.game.game_state.ended:
            # determine the next player
            next_to_play = self.game.game_state.get_next_player()

            # get the next move from the player
            coord, card = self.players[next_to_play].get_move(
                self.game.game_state)
            

            # notify the listeners that player has made a move
            self.dispatch_event(PlayerMoveEvent(
                coord,
                card,
                initiating_player=next_to_play,
            ))

            # actually place the card on the board
            self.game.place_card(coord[0], coord[1], card)

        # game ended, notify the listeners
        self.dispatch_event(GameEndEvent(self.game.game_state))

        # get and return the final scores
        final_scores = self.game.game_state.get_scores()
        return final_scores

    def _on_coinflip_result(self, attack_event: AttackEvent, favored_player: int):
        # notify the listeners that the coinflip has been resolved
        self.dispatch_event(CoinflipEvent(attack_event, favored_player))

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


if __name__ == "__main__":
    from ai.random_ai import RandomAI
    from ai.heuristic_ai import SimpleHeuristicAI

    # player_1 = HumanTarockPlayer()
    # player_1 = SimpleHeuristicAI(attack_coefficient=1, defense_coefficient=1, presence_coefficient=1)
    player_1 = RandomAI()

    # player_2 = RandomAI()
    player_2 = SimpleHeuristicAI(attack_coefficient=1, defense_coefficient=1, presence_coefficient=5)

    controller = TarockGameController(player_1, player_2)
    # controller.register_event_listener(player_1, 0)

    # controller = TarockGameController(HumanTarockPlayer(), HumanTarockPlayer())
    # controller = TarockGameController(RandomAI(), SimpleHeuristicAI(attack_coefficient=1, defense_coefficient=1, presence_coefficient=10))
    # controller = TarockGameController(SimpleHeuristicAI(attack_coefficient=1, defense_coefficient=1, presence_coefficient=1), SimpleHeuristicAI(attack_coefficient=1, defense_coefficient=1, presence_coefficient=10))

    win_counts = [0, 0]
    for _ in trange(1000):
        final_scores = controller.start_new_game(fair_start=True, starting_player=0)
        winner = 0 if final_scores[0] > final_scores[1] else 1
        win_counts[winner] += 1

    print(f"Player 1 won {win_counts[0]} times")
    print(f"Player 2 won {win_counts[1]} times")
