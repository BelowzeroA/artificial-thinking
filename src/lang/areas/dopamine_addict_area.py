from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea


class DopamineAddictArea(NeuralArea):
    """
    Constantly pulses until being cooled by a portion of dopamine
    """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.satisfied_state_ticks = []

    def receive_dope(self):
        current_tick = self.agent.environment.current_tick
        self.satisfied_state_ticks.extend(
            range(current_tick + 1, current_tick + HyperParameters.dopamine_addict_satisfaction_span + 1))

    def before_assemblies_update(self, tick: int):
        if tick not in self.satisfied_state_ticks:
            self.agent.queue_message('dope_yearning', data={'zone': self.zone})

