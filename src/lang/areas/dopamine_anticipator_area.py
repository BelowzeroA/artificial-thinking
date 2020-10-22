from lang.areas.rule_area import RuleArea
from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly


class DopamineAnticipatorArea(NeuralArea):
    """
    Anticipates dopamine influx after rule firing
    """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.allows_projection = True
        self.cortisol_starting_tick = 0

    def receive_dope(self):
        self.cortisol_starting_tick = 0

    def on_assembly_created(self, na: NeuralAssembly):
        # Unilateral activation from a rule assembly will be established later, upon activation
        connections = self.agent.container.get_assembly_incoming_connections(na)
        from_rule_connections = [c for c in connections if isinstance(c.source.area, RuleArea)]
        from_rule_connections[0].multiplier = 1

    def on_fire(self, na: NeuralAssembly):
        self.cortisol_starting_tick = self.agent.environment.current_tick + 3

    def before_assemblies_update(self, tick: int):
        if tick == self.cortisol_starting_tick:
            self.agent.stressed_ticks.append(tick)


