from game import AttackEvent

class CoinflipListenerMixin:
    def on_coinflip_result(self, attack_event: AttackEvent, favored_player: int):
        raise NotImplementedError("process_coinflip not implemented")