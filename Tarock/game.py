
from dataclasses import dataclass
from enum import Enum, Flag
import random
from typing import List, Optional, Tuple, Set

# from coinflip_listener import CoinflipListenerMixin
# from ALL_CARDS import ALL_CARDS, name_to_cardinfo


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    def opposite(self):
        if self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.DOWN:
            return Direction.UP
        elif self == Direction.LEFT:
            return Direction.RIGHT
        elif self == Direction.RIGHT:
            return Direction.LEFT
        
    def __str__(self):
        if self == Direction.UP:
            return "⬆️"
        elif self == Direction.DOWN:
            return "⬇️"
        elif self == Direction.LEFT:
            return "⬅️"
        elif self == Direction.RIGHT:
            return "➡️"
    
    @staticmethod 
    def all_directions():
        return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]

class Card:
    '''
    A card in the game.

    Attributes:
        attack: The attack value of the card.
        defense: The defense value of the card.
        name: The name of the card.
        directions: The directions this card "overpowers". 
            When attacking: the card ignores the defense of the cards in these directions. If the card being attacked doesn't have a defense in the opposite direction, the attack is automatically successful. Otherwise, the outcome depends on a coin toss.
            When defending: the card ignores the attack of the cards in these directions. If the card being attacked doesn't have an attack in the opposite direction, the attack is automatically failed. Otherwise, the outcome depends on a coin toss.
    '''
    def __init__(self, attack: int, defense: int, name: str, directions: List[Direction]):
        self.attack = attack
        self.defense = defense
        self.name = name
        self.directions = directions

    def __str__(self):
        return f"{self.name} (🗡️ {self.attack} 🛡️ {self.defense})"

    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        return (self.attack == other.attack and self.defense == other.defense and self.directions == other.directions) or self.name == other.name
    
    @staticmethod
    def get_card_based_on_cardinfo(cardinfo):
        return Card(cardinfo.attack, cardinfo.defense, cardinfo.name, cardinfo.directions)
    
    @staticmethod
    def get_random_card(ALL_CARDS):
        return Card.get_card_based_on_cardinfo(random.choice(ALL_CARDS))

class Cell:
    '''
    A cell in the game board. Can be either empty or occupied by a card.
    '''
    def __init__(self, card: Optional[Card] = None, owner: int = -1):
        self.card = card
        self.owner = owner

    def __str__(self):
        return str(self.card) + f"*{self.owner+1}" if self.card is not None else "Empty"

class Board:
    '''
    The board of the game. Contains 9 cells in a 3x3 grid, each of which can hold a card. Each cell can be either empty or occupied by a card. A cell which is occupied by a card must have a owner, which is one of the players.
    '''
    def __init__(self):
        self.cells = [[Cell() for _ in range(3)] for _ in range(3)]

    def is_cell_empty(self, row, col):
        return self.cells[row][col].card is None

    def get_cell_value(self, coord: Tuple[int, int]):
        return self.cells[coord[0]][coord[1]]

    def get_cell_owner(self, coords: Tuple[int, int]):
        row, col = coords
        return self.cells[row][col].owner if self.cells[row][col].card is not None else None
    
    def get_empty_coords(self):
        empty_coords = []
        for row in range(3):
            for col in range(3):
                if self.is_cell_empty(row, col):
                    empty_coords.append((row, col))
        return empty_coords
    
    def __str__(self) -> str:
        # generate a pretty representation of the board with 3 rows and 3 columns, each cell in 20 characters wide

        # first, generate the top border
        board_str = "┌"+"─"*20+"┬"+"─"*20+"┬"+"─"*20+"┐\n"

        # then, generate the rows
        for row in range(3):
            for i in range(5):
                board_str += "│"
                for col in range(3):
                    cell = self.cells[row][col]
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

        return board_str


    
    @staticmethod
    def get_adj_coord_in_direction(coord: Tuple[int, int], direction: Direction):
        if direction == Direction.UP:
            temp_coord = (coord[0] - 1, coord[1])
        elif direction == Direction.DOWN:
            temp_coord = (coord[0] + 1, coord[1])
        elif direction == Direction.LEFT:
            temp_coord = (coord[0], coord[1] - 1)
        elif direction == Direction.RIGHT:
            temp_coord = (coord[0], coord[1] + 1)

        if temp_coord[0] < 0 or temp_coord[0] > 2 or temp_coord[1] < 0 or temp_coord[1] > 2:
            raise ValueError("The cell is out of bounds.")
        else:
            return temp_coord
        
    @staticmethod
    def get_direction_of_other_about_this(this: Tuple[int, int], other: Tuple[int, int]):
        if other[0] == this[0]:
            if other[1] == this[1] + 1:
                return Direction.RIGHT
            elif other[1] == this[1] - 1:
                return Direction.LEFT
        elif other[1] == this[1]:
            if other[0] == this[0] + 1:
                return Direction.DOWN
            elif other[0] == this[0] - 1:
                return Direction.UP
        raise ValueError("The cells are not adjacent.")

    @staticmethod
    def get_fresh_board():
        return Board()

class GameState:
    '''
    The state of the game. Contains the board and the hands of the players.
    '''
    def __init__(self, board: Board , player_hands: Tuple[List[Card],List[Card]], next_player: int, terminal: bool = False):
        self.board = board
        self.player_hands = player_hands
        self.next_player = next_player
        self.ended = terminal

    def get_player_hand(self, player: int):
        return self.player_hands[player]
    
    def get_next_player(self):
        return self.next_player
    
    def get_board(self):
        return self.board
    
    def is_terminal(self):
        '''
        Returns True if the this represents a terminal state, i.e. the game is over. The game is over if the board is full.
        '''
        is_terminal_state = True
        for row in range(3):
            for col in range(3):
                if self.board.is_cell_empty(row, col):
                    is_terminal_state = False
                    break
        return is_terminal_state
    
    def get_scores(self):
        '''
        Returns the scores of the players. The score of a player is the totally number of cards they own on the board.
        '''
        scores = [0, 0]
        for row in range(3):
            for col in range(3):
                owner = self.board.get_cell_owner((row, col))
                if owner is not None:
                    scores[owner] += 1
        return scores
    

class AttackEvent:
    '''
    An event in the game, defined as an attack of a card to another card, (with the potential to change the state of the board).
    '''
    def __init__(self, attacker: Card, defender: Card, attacker_coords: Tuple[int, int], defender_coords: Tuple[int, int], intiating_player: int):
        self.attacker = attacker
        self.defender = defender
        self.attacker_coords = attacker_coords
        self.defender_coords = defender_coords
        self.intiating_player = intiating_player

class Game:
    '''
    The game itself.
    '''

    def __init__(self, starting_player: int, starting_hands: Tuple[List[Card],List[Card]], coinflip_listeners: Set = set()):
        self.game_state = GameState(Board.get_fresh_board(), starting_hands, starting_player)
        self.coinflip_listeners = coinflip_listeners

    def get_game_state(self):
        return self.game_state
    
    def register_coinflip_listener(self, listener):
        self.coinflip_listeners.add(listener)
    
    def get_coinflip_result(self, event: AttackEvent):
        favored_player = random.randint(0, 1)
        for listener in self.coinflip_listeners:
            listener._on_coinflip_result(event, favored_player)
        return favored_player
    
    def place_card(self, row: int, col: int, card: Card):
        '''
        Plays a card on the board. The card is placed on the given cell and the cell is marked as owned by the given player.
        '''
        
        # TODO: legality check: is the cell empty? is the card in the player's hand? 

        player = self.game_state.next_player

        # place the card on the board and remove it from the player's hand
        self.game_state.board.cells[row][col].card = card
        self.game_state.board.cells[row][col].owner = player
        self.game_state.player_hands[player].remove(card)

        # generate the events that this card causes
        attack_events = self._generate_attack_events((row, col), card, player)
        for attack_event in attack_events:
            self._resolve_attack_event(attack_event)

        # change the next player
        self.game_state.next_player = 1 - self.game_state.next_player

        # check if the game is over
        self.game_state.ended = self.game_state.is_terminal()

    def _generate_attack_events(self, attacker_coord: Tuple[int, int] , attacking_card: Card, attacking_player: int):
        '''
        Generates the attack events that this card causes.
        '''
        events = []
        for direction in Direction.all_directions():

            # get the defense cell in the given direction
            try:
                defense_cell_coords = Board.get_adj_coord_in_direction(attacker_coord, direction)
                defense_cell = self.game_state.board.get_cell_value(defense_cell_coords)
            except ValueError:
                continue

            # if the defense cell is empty, no event is generated
            if defense_cell.card is None:
                continue

            # if the defense cell is owned by the attacking player, no event is generated
            if defense_cell.owner == attacking_player:
                continue

            # if the defense cell is owned by the other player, an event is generated
            new_event = AttackEvent(attacking_card, defense_cell.card, attacker_coord, defense_cell_coords, attacking_player)
            events.append(new_event)

        return events
    
    def _resolve_attack_event(self, attack_event: AttackEvent):
        '''
        Resolves an event. Nothing happens if the attack is unsuccessful. If the attack is successful, the defender's ownership is transfered to the attacker.
        '''
        attack_successful = self._determine_attack_event_outcome(attack_event)
        if attack_successful:
            defender_cell = self.game_state.board.get_cell_value(attack_event.defender_coords)
            defender_cell.owner = attack_event.intiating_player


    def _determine_attack_event_outcome(self, event: AttackEvent):
        '''
        Resolves an event.
        '''
        # determine the attack and defense directions and check for overpowering
        attack_direction = Board.get_direction_of_other_about_this(event.attacker_coords, event.defender_coords)
        defense_direction = Board.get_direction_of_other_about_this(event.defender_coords, event.attacker_coords)
        attack_overpower = attack_direction in event.attacker.directions
        defense_overpower = defense_direction in event.defender.directions

        # attack is unsuccessful by default
        attack_successful = False

        # if both overpower, coin flip to determine outcome
        if attack_overpower and defense_overpower:
            favored_player = self.get_coinflip_result(event)
            attack_successful = favored_player == event.intiating_player

        # if only the attack overpowers, the attack is successful
        elif attack_overpower:
            attack_successful = True

        # if only the defense overpowers, the attack is unsuccessful
        elif defense_overpower:
            attack_successful = False

        # if neither overpower, compare the attack and defense values
        else:
            attack_advantage = event.attacker.attack - event.defender.defense
            if attack_advantage > 0:
                attack_successful = True
            elif attack_advantage < 0:
                attack_successful = False
            else:
                favored_player = self.get_coinflip_result(event)
                attack_successful = favored_player == event.intiating_player

        return attack_successful

            


                
        




    

    

    
    


    
