from game import AttackEvent

class CoinflipListener:
    def _on_coinflip_result(self, attack_event: AttackEvent, successful: bool):
        raise NotImplementedError("process_coinflip not implemented")
    
class ConflipManipulator:
    def determine_coinflip_outcome(self, attack_event: AttackEvent) -> bool:
        raise NotImplementedError("process_coinflip not implemented")