from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly


class DopamineAddictArea(NeuralArea):
    """
    Constantly pulses until being cooled by a portion of dopamine
    Corresponds to Striatum
    """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.satisfied_state_ticks = []
        self.assembly_firing_counter = {}
        self.allows_projection = True

    def receive_dope(self):
        current_tick = self.agent.environment.current_tick
        self.satisfied_state_ticks.extend(
            range(current_tick + 1, current_tick + HyperParameters.dopamine_addict_satisfaction_span + 1))

    def on_fire(self, na: NeuralAssembly):
        current_tick = self.agent.environment.current_tick
        if current_tick in self.satisfied_state_ticks:
            return
        if na not in self.assembly_firing_counter:
            self.assembly_firing_counter[na] = 0
        self.assembly_firing_counter[na] += 1
        if self.assembly_firing_counter[na] < 5:
            self.agent.queue_message('dope_yearning', data={'zone': self.zone})

    # def before_assemblies_update(self, tick: int):
    #     if tick not in self.satisfied_state_ticks:
    #         self.agent.queue_message('dope_yearning', data={'zone': self.zone})

