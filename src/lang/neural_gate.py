from typing import List, Set

from lang.connection import Connection
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly


class NeuralGate:
    """
    Neural gate is a simple area acting as a bridge between two neural areas.
    If it's open, it lets an assembly pass through to a receiving area
    """
    def __init__(self, agent: 'Agent', source: NeuralArea, target: NeuralArea):
        self.source = source
        self.target = target
        self.agent = agent
        self.connection = None
        self.controller = None
        if source not in target.exciting_areas:
            raise ValueError(f'Areas {source} and {target} are not connected')
        self.open_at_ticks = []

    def is_open(self, connection: Connection) -> bool:
        current_tick = self.agent.environment.current_tick
        if current_tick in self.open_at_ticks:
            return True
        else:
            # Workaround to let an assembly pass no matter what if a complete path
            # of the assembly didn't make it yet to the final area
            # TODO: remove this ugly crutch ASAP
            final_area = self.agent.container.find_zone('SpProd').input_area
            final_area_assemblies = final_area.get_assemblies()
            ans = [an for an in final_area_assemblies if an.is_successor_of(connection.target)]
            if not any(ans):
                return True
        return False

    def on_assembly_pass(self, na: NeuralAssembly):
        if self.controller:
            self.controller.on_assembly_pass(na)

    def _repr(self):
        return f'({self.source} - {self.target})'

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()
