from lang.areas.action_area import ActionArea
from lang.areas.observation_integrator_area import ObservationIntegratorArea
from lang.areas.rule_area import RuleArea
from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly


class RuleInhibitorArea(NeuralArea):
    """
    Provides GABA flow to the target area
    """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.allows_assembly_merging = True
        self.rule_area = None

    def before_assemblies_update(self, tick: int):
        pass

    def receive_cortisol(self):
        # stress-induced GABAergic inhibition
        current_tick = self.agent.environment.current_tick
        recently_active_rules = [na for na in self.agent.container.assemblies
                                 if na.last_fired_at >= current_tick - 1 and na.area == self.rule_area]
        for rule in recently_active_rules:
            self.deactivate_rule(rule)
        recently_active_inhibitors = [na for na in self.agent.container.assemblies
                                 if na.last_fired_at >= current_tick - 1 and na.area == self]
        for inhibitor in recently_active_inhibitors:
            self.activate_inhibitor(inhibitor)

    def deactivate_rule(self, rule_assembly: NeuralAssembly):
        rule_assembly.activated = False
        connections = self.agent.container.get_assembly_incoming_connections(rule_assembly)
        observation_rule_connections = [c for c in connections if isinstance(c.source.area, ObservationIntegratorArea)]
        # Unilateral activation from an Observer
        observation_rule_connections[0].multiplier = 1
        print(f'rule {rule_assembly} deactivated')

    def activate_inhibitor(self, assembly: NeuralAssembly):
        connections = self.agent.container.get_assembly_incoming_connections(assembly)
        observation_connections = [c for c in connections if isinstance(c.source.area, ObservationIntegratorArea)]
        # Unilateral activation from an Observer
        observation_connections[0].multiplier = 2

        action_connections = [c for c in connections if isinstance(c.source.area, ActionArea)]
        action_connection = action_connections[0]
        # to avoid backward activation
        action_connection.multiplier = 0

        action = action_connection.source

        # Connect the the inhibitor and the action
        inhibitor_action_connection = self.agent.assembly_builder.check_create_connection(
            source=assembly, target=action)
        inhibitor_action_connection.multiplier = -1

