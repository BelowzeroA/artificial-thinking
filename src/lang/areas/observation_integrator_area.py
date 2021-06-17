from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly


class ObservationIntegratorArea(NeuralArea):
    """
    Integrates outgoing assemblies from different zones to a single compound assembly
    """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.allows_assembly_merging = True
        self.allows_projection = True
        self.winner_takes_it_all_strategy = True

    def before_assemblies_update(self, tick: int):
        assemblies = [na for na in self.agent.container.assemblies if na.area == self and na.potential > 0]
        for assembly in assemblies:
            assembly.potential += 2 if assembly.is_joint else 0
        self.check_set_is_winner(threshold=HyperParameters.phonetic_recognition_threshold)

    def on_fire(self, na: NeuralAssembly):
        self.zone.on_observation_arrive(na)
        # implements a prolonged firing pattern
        current_tick = self.agent.environment.current_tick
        if current_tick not in na.firing_ticks:
            na.firing_ticks.extend(range(current_tick + 1, current_tick + 3))


