from lang.areas.action_area import ActionArea
from lang.areas.dopamine_addict_area import DopamineAddictArea
from lang.areas.dopamine_anticipator_area import DopamineAnticipatorArea
from lang.areas.observation_integrator_area import ObservationIntegratorArea
from lang.areas.rule_area import RuleArea
from lang.areas.rule_inhibitor_area import RuleInhibitorArea
from lang.neural_gate import NeuralGate
from lang.neural_zone import NeuralZone


class SpeechControllerZone(NeuralZone):
    """
    Controls other zones gating (inhibition/activation) to allow speech production
    Corresponds to the Ventro-Lateral Pre-Frontal Cortex (VLPFC)
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'SpCntr'
        self.num_areas = 1
        self.rules = []
        self.actions = []
        self.inhibitors = []
        self.dopamine_addict = None
        self.observation_integrator = None
        self.dopamine_anticipator = None
        self.prepare_areas()

    def prepare_areas(self):
        self.observation_integrator = ObservationIntegratorArea.add('observator', agent=self.agent, zone=self)
        self.dopamine_addict = DopamineAddictArea.add('dope_addict', agent=self.agent, zone=self)
        self.dopamine_addict.add_exciting_area(self.observation_integrator)
        self.dopamine_anticipator = DopamineAnticipatorArea.add('dope_anticipator', agent=self.agent, zone=self)
        for i in range(self.num_areas):
            rule_area = RuleArea.add(f'rule{i}', agent=self.agent, zone=self)
            rule_area.add_exciting_area(self.observation_integrator)
            action_area = ActionArea.add(f'action{i}', agent=self.agent, zone=self)
            action_area.add_exciting_area(rule_area)
            action_area.add_exciting_area(self.dopamine_addict)
            rule_area.add_exciting_area(action_area)

            self.dopamine_anticipator.add_exciting_area(rule_area)

            inhibitor_area = RuleInhibitorArea.add(f'inhibitor{i}', agent=self.agent, zone=self)
            inhibitor_area.rule_area = rule_area
            self.inhibitors.append(inhibitor_area)
            inhibitor_area.add_exciting_area(self.observation_integrator)
            inhibitor_area.add_exciting_area(action_area)

            action_area.add_inhibiting_area(inhibitor_area)
            # rule_area.add_inhibiting_area(inhibitor_area)

            self.rules.append(rule_area)
            self.actions.append(action_area)

    def build_predefined_assemblies(self):
        for action_area in self.actions:
            action_area.build_predefined_assemblies()

    def connect_to_sensors(self, areas):
        for area in areas:
            self.observation_integrator.add_exciting_area(area)

    def connect_to_gate(self, gate: NeuralGate):
        for action_area in self.actions:
            action_area.gates.append(gate)

    def prepare_assemblies(self, source, tick: int):
        pass

    def before_assemblies_update(self, tick: int):
        #self.dopamine_addict.before_assemblies_update(tick)
        self.dopamine_anticipator.before_assemblies_update(tick)
        self.observation_integrator.before_assemblies_update(tick)

    def receive_dope(self):
        self.dopamine_addict.receive_dope()
        for rule_area in self.rules:
            rule_area.receive_dope()

    def receive_cortisol(self):
        for inhibitor_area in self.inhibitors:
            inhibitor_area.receive_cortisol()