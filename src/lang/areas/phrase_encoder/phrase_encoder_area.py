from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea


class PhraseEncoderArea(NeuralArea):
    """
     Represents all crutches for the zone
     """
    def __init__(self, name: str, agent, zone):
        from lang.assembly_builder import AssemblyBuilder
        super().__init__(name, agent, zone)
        self.phonetics = {}
        self.threshold = HyperParameters.phonetic_recognition_threshold
        self.builder: AssemblyBuilder = None
        self.winner_takes_it_all_strategy = False
        self.allows_assembly_merging = True
        self.inhibits_itself = False

    def on_fire(self, na: 'NeuralAssembly'):
        super().on_fire(na)
        inhibited_areas = [a for a in self.agent.container.areas if self in a.inhibiting_areas]
        target_tick = self.agent.environment.current_tick + 1
        for area in inhibited_areas:
            area.inhibited_at_ticks.append(target_tick)
        if self.inhibits_itself:
            self.inhibited_at_ticks.append(target_tick)

    def allow_firing(self, na: 'NeuralAssembly') -> bool:
        if na.pattern.startswith('ph:'):
            return False
        return True