from tarock_player import TarockBasePlayer
from game import *
from pprint import pprint

class GameEvent:
    def __init__(self, event_data):
        if event_data is None:
            raise ValueError("event_data cannot be None")
        self.event_data = event_data

class GameStartEvent(GameEvent):
    def __init__(self, starting_state: GameState):
        super().__init__(starting_state)

class GameEndEvent(GameEvent):
    def __init__(self, final_state: GameState):
        event_data = final_state
        super().__init__(event_data)

class CoinflipEvent(GameEvent):
    def __init__(self, attack_event: AttackEvent, successful: int):
        event_data = (attack_event, successful)
        super().__init__(event_data)

class PlayerMoveEvent(GameEvent):
    def __init__(self, coords: Tuple[int, int], card: Card, initiating_player: int):
        event_data = (coords, card, initiating_player)
        super().__init__(event_data)


class BaseGameEventListener():
    def _on_game_event(self, event: GameEvent):
        raise NotImplementedError("process_game_event not implemented")
    
class PrintGameEventsMixin(BaseGameEventListener):
    def _on_game_event(self, event: GameEvent):
        if isinstance(event, GameStartEvent):
            starting_state = event.event_data
            self._print_on_game_start(starting_state)
        elif isinstance(event, GameEndEvent):
            final_state = event.event_data
            self._print_on_game_end(final_state)
        elif isinstance(event, CoinflipEvent):
            attack_event, favored_player = event.event_data
            self._print_on_coinflip_result(attack_event, favored_player)
        elif isinstance(event, PlayerMoveEvent):
            coords, card, initiating_player = event.event_data
            self._print_on_player_move(coords, card, initiating_player)
        else:
            raise NotImplementedError("process_game_event not implemented")
        
    def _print_on_game_start(self, starting_state: GameState):
        print("Welcome to Tarock! Starting a new game...")
        print("\nPlayer 1's hand: ")
        pprint(starting_state.player_hands[0])
        print("\nPlayer 2's hand: ")
        pprint(starting_state.player_hands[1])
        print(f"\nStarting player: {starting_state.get_next_player()+1}")

    def _print_on_game_end(self, final_state: GameState):

        # Get scores and calculate winner
        final_scores = final_state.get_scores()
        winner = 0 if final_scores[0] > final_scores[1] else 1

        print("\nFinal scores:")
        print(f"Player 1: {final_scores[0]}")
        print(f"Player 2: {final_scores[1]}")
        print(f"\nWinner: Player {winner+1}")
        print("\nFinal Board:")
        final_board = final_state.board
        print(final_board)

    def _print_on_coinflip_result(self, attack_event: AttackEvent, successful: bool):
        attacker = attack_event.attacker
        defender = attack_event.defender
        attacker_coords = attack_event.attacker_coords
        defender_coords = attack_event.defender_coords
        print(
            f"\nCoin flip required for {attacker.name} ({attacker_coords[0]}, {attacker_coords[1]}) attacking {defender.name} ({defender_coords[0]}, {defender_coords[1]})")
        if successful:
            print("\nAttack successful!")
        else:
            print("\nAttack failed!")

    def _print_on_player_move(self, coords: Tuple[int, int], card: Card, initiating_player: int):
        print(f"\nPlayer {initiating_player + 1} places {card} at ({coords[0]}, {coords[1]})")



