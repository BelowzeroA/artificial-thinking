from lang.areas.action_area import ActionArea
from lang.areas.observation_integrator_area import ObservationIntegratorArea
from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly


class RuleArea(NeuralArea):
    """
    Connects observers and actions (sensors and actuators in terms of robotics)
    """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.allows_assembly_merging = True

    def before_assemblies_update(self, tick: int):
        pass

    def activate_rule(self, rule_assembly: NeuralAssembly):
        connections = self.agent.container.get_assembly_incoming_connections(rule_assembly)
        observation_rule_connections = [c for c in connections if isinstance(c.source.area, ObservationIntegratorArea)]
        # Unilateral activation from an Observer
        observation_rule_connections[0].multiplier = 2

        action_rule_connections = [c for c in connections if isinstance(c.source.area, ActionArea)]
        action_rule_connection = action_rule_connections[0]
        # to avoid backward activation
        action_rule_connection.multiplier = 0

        action = action_rule_connection.source

        # Connect the rule and the action
        rule_action_connection = self.agent.assembly_builder.check_create_connection(
            source=rule_assembly, target=action)
        rule_action_connection.multiplier = 2

    def receive_dope(self):
        current_tick = self.agent.environment.current_tick
        recently_active_rules = [na for na in self.agent.container.assemblies
                                 if na.last_fired_at >= current_tick - 1 and na.area == self]
        for rule in recently_active_rules:
            self.activate_rule(rule)





