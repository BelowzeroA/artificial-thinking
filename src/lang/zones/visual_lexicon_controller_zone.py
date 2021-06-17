from lang.neural_assembly import NeuralAssembly
from lang.neural_gate import NeuralGate
from lang.zones.controller_zone import ControllerZone


class VisualLexiconControllerZone(ControllerZone):
    """
    Bridges the visual lexicon and the speech producer.
    Used to generalize phrases
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'VL_controller'
        self.working_memory = {}
        self.rules = []
        self.gate = None
        self.passed_a = {}

    def prepare_areas(self):
        super().prepare_areas()

    def output_areas(self):
        return [self.output]

    def connect_to_gate(self, gate: NeuralGate):
        self.gate = gate
        self.gate.controller = self

    def on_master_action_fire(self, na: NeuralAssembly):
        self.set_working_memory(na.pattern)

    def connect_to_master_action(self, master_zone: ControllerZone):
        master_zone.output.callbacks.append(self.on_master_action_fire)

    def on_observation_arrive(self, na: NeuralAssembly):
        current_tick = self.agent.environment.current_tick
        self.gate.open_at_ticks = list(range(current_tick, current_tick + 2))
        
    def set_working_memory(self, value: str):
        current_tick = self.agent.environment.current_tick
        self.working_memory[current_tick] = value

    def on_assembly_pass(self, na: NeuralAssembly):
        attempted_tick = self.agent.environment.current_tick - 3
        phonetic_pattern = na.get_phonetic_pattern()
        self.passed_a[attempted_tick] = phonetic_pattern
        if attempted_tick in self.working_memory:
            if phonetic_pattern == self.working_memory[attempted_tick]:
                self.rules.append(phonetic_pattern)


