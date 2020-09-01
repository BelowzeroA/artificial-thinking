from typing import List, Set

from lang.neural_area import NeuralArea


class NeuralGate:
    """
    Neural gate is a simple area acting as a bridge between two neural areas.
    If it's open, it lets an assembly pass through to a receiving area
    """
    def __init__(self, agent: 'Agent', source: NeuralArea, target: NeuralArea):
        self.source = source
        self.target = target
        self.agent = agent
        if source not in target.exciting_areas:
            raise ValueError(f'Areas {source} and {target} are not connected')
        self.inhibited_at_ticks = []

    @property
    def is_open(self) -> bool:
        return True

    def _repr(self):
        return f'[{self.source} - {self.target}]'

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()
