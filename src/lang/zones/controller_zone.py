
from lang.areas.observation_integrator_area import ObservationIntegratorArea
from lang.neural_assembly import NeuralAssembly
from lang.neural_gate import NeuralGate
from lang.neural_zone import NeuralZone


class ControllerZone(NeuralZone):
    """
    Abstract controller zone. To be implemented by endpoint control zones that control gates and speech primitives
    """
    def __init__(self, agent: 'Agent', name: str):
        super().__init__(name=name, agent=agent)
        self.observation_integrator = None
        self.prepare_areas()

    def prepare_areas(self):
        self.observation_integrator = ObservationIntegratorArea.add('observator', agent=self.agent, zone=self)

    def build_predefined_assemblies(self):
        return
        for action_area in self.actions:
            action_area.build_predefined_assemblies()

    def on_observation_arrive(self, na: NeuralAssembly):
        pass

    def connect_to_sensors(self, areas):
        for area in areas:
            self.observation_integrator.add_exciting_area(area)

    def connect_to_gate(self, gate: NeuralGate):
        return
        for action_area in self.actions:
            action_area.gates.append(gate)

    def prepare_assemblies(self, source, tick: int):
        pass

    def before_assemblies_update(self, tick: int):
        self.observation_integrator.before_assemblies_update(tick)

    def receive_dope(self):
        return
        self.dopamine_addict.receive_dope()
        for rule_area in self.rules:
            rule_area.receive_dope()

    def receive_cortisol(self):
        return
        for inhibitor_area in self.inhibitors:
            inhibitor_area.receive_cortisol()