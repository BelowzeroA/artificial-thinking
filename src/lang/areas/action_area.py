import random

from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly
from lang.neural_gate import NeuralGate
from lang.primitives.inter_area_message import InterAreaMessage

NO_GATE = 'NO_GATE'


class ActionArea(NeuralArea):
    """
    Connects rule areas with the areas affected by the action
    """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.gates = [NO_GATE]
        self.assemblies = []
        self.actuated_assemblies = {}

    def before_assemblies_update(self, tick: int):
        pass

    def build_predefined_assemblies(self):
        for gate in self.gates:
            # if isinstance(gate, str):
                na = self.agent.assembly_builder.find_create_assembly(str(gate), area=self)
                na.gate = gate
                self.assemblies.append(na)

    def on_fire(self, na: NeuralAssembly):
        current_tick = self.agent.environment.current_tick
        if issubclass(type(na.gate), NeuralGate):
            na.gate.open_at_ticks.append(current_tick + 1)

    def handle_message(self, msg: InterAreaMessage):
        current_tick = self.agent.environment.current_tick
        if msg.name == 'dope_yearning' and msg.data['zone'] == self.zone:
            if current_tick not in self.actuated_assemblies:
                assembly = random.choice(self.assemblies)
                for i in range(current_tick, current_tick + HyperParameters.gate_opening_period):
                    self.actuated_assemblies[i] = assembly
                    assembly.firing_ticks.append(i)
