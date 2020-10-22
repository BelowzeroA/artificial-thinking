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

    def before_assemblies_update(self, tick: int):
        pass

    def on_fire(self, na: NeuralAssembly):
        current_tick = self.agent.environment.current_tick
        if current_tick not in na.firing_ticks:
            na.firing_ticks.extend(range(current_tick + 1, current_tick + 3))


