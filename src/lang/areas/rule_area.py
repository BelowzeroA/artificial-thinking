from typing import List

from lang.areas.action_area import ActionArea
from lang.areas.observation_integrator_area import ObservationIntegratorArea
from lang.connection import Connection
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

    def allow_firing(self, na: NeuralAssembly):
        return True
        # return na.activated

    def activate_rule(self, rule_assembly: NeuralAssembly):
        rule_assembly.activated = True
        incoming_connections = self.agent.container.get_assembly_incoming_connections(rule_assembly)
        outgoing_connections = self.agent.container.get_assembly_outgoing_connections(rule_assembly)

        # Unilateral activation from an Observer
        self.activate_observation_rule_connection(incoming_connections)

        # to avoid backward activation
        action_assembly = self.deactivate_action_rule_connection(incoming_connections)

        # Connect the rule and the action
        self.connect_rule_with_action(rule_assembly, action_assembly)

        # strengthen a connection from the rule to the dopamine-anticipator assembly
        self.activate_rule_dopamine_anticipator_connection(outgoing_connections)

        print(f'rule {rule_assembly} activated')

    @staticmethod
    def activate_observation_rule_connection(connections: List[Connection]):
        observation_rule_connections = [c for c in connections if isinstance(c.source.area, ObservationIntegratorArea)]
        observation_rule_connections[0].multiplier = 2
    
    @staticmethod
    def activate_rule_dopamine_anticipator_connection(connections: List[Connection]):
        from lang.areas.dopamine_anticipator_area import DopamineAnticipatorArea
        conns = [c for c in connections if isinstance(c.target.area, DopamineAnticipatorArea)]
        conns[0].multiplier = 2
        
    @staticmethod
    def deactivate_action_rule_connection(connections: List[Connection]):
        action_rule_connections = [c for c in connections if isinstance(c.source.area, ActionArea)]
        action_rule_connection = action_rule_connections[0]
        action_rule_connection.multiplier = 0
        return action_rule_connection.source

    def connect_rule_with_action(self, rule_assembly: NeuralAssembly, action_assembly: NeuralAssembly):
        rule_action_connection = self.agent.assembly_builder.check_create_connection(
            source=rule_assembly, target=action_assembly)
        rule_action_connection.multiplier = 2

    def receive_dope(self):
        current_tick = self.agent.environment.current_tick
        recently_active_rules = [na for na in self.agent.container.assemblies
                                 if na.last_fired_at >= current_tick - 1 and na.area == self]
        for rule in recently_active_rules:
            self.activate_rule(rule)





