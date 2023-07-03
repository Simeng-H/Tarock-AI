from game import *
import copy

class TarockAI:
    def get_move(self, game_state: GameState) -> Tuple[Tuple[int, int], Card]:
        '''
        Provided the current game state, return a move to make, in the form of a tuple of the form:
        ((row, col), card)
        '''
        raise NotImplementedError("get_move not implemented")

    @staticmethod
    def simulate_move(coords: Tuple[int, int], card: Card, current_state: GameState) -> GameState:
        '''
        Simulates placing a card on the board. The card is placed on the given cell and the cell is marked as owned by the given player. Returns a new game state with the new board.
        '''
        temp_state = copy.deepcopy(current_state)

        # HACK: find the card in the player's hand,
        copied_card = card
        for c in temp_state.player_hands[temp_state.get_next_player()]:
            if c == card:
                copied_card = c
                break

        # place the card on the board and remove it from the player's hand
        temp_state.board.cells[coords[0]][coords[1]].card = card
        temp_state.board.cells[coords[0]][coords[1]].owner = temp_state.get_next_player()
        temp_state.player_hands[temp_state.get_next_player()].remove(copied_card)

        # generate the events that this card causes
        attack_events = TarockAI._generate_attack_events_for_placement(coords, copied_card, temp_state.get_next_player(), temp_state.board)
        for attack_event in attack_events:
            TarockAI._resolve_attack_event(attack_event, temp_state.board)

        # change the next player
        temp_state.next_player = 1 - temp_state.next_player

        return temp_state

    @staticmethod
    def _generate_attack_events_for_placement(coords: Tuple[int, int], card: Card, player: int, board: Board):
        '''
        Generates the attack events that this card causes.
        '''
        events = []
        for direction in Direction.all_directions():

            # get the defense cell in the given direction
            try:
                defense_cell_coords = Board.get_cell_in_direction(coords, direction)
                defense_cell = board.get_cell_value(defense_cell_coords)
            except ValueError:
                continue

            # if the defense cell is empty, no event is generated
            if defense_cell.card is None:
                continue

            # if the defense cell is owned by the attacking player, no event is generated
            if defense_cell.owner == player:
                continue

            # if the defense cell is owned by the other player, an event is generated
            new_event = AttackEvent(card, defense_cell.card, coords, defense_cell_coords, player)
            events.append(new_event)

        return events
    
    @staticmethod
    def _resolve_attack_event(event: AttackEvent, board: Board):
        '''
        Resolves an event. Nothing happens if the attack is unsuccessful. If the attack is successful, the defender's ownership is transfered to the attacker.
        '''
        attack_successful = TarockAI._determine_attack_event_outcome(event)
        if attack_successful:
            defender_cell = board.get_cell_value(event.defender_coords)
            defender_cell.owner = event.intiating_player

    @staticmethod
    def _determine_attack_event_outcome(event: AttackEvent) -> bool:
        '''
        Determines the outcome of an attack event.
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
            favored_player = random.randint(0, 1)
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
                favored_player = random.randint(0, 1)
                attack_successful = favored_player == event.intiating_player

        return attack_successful