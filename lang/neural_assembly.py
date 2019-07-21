from typing import List

from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea


class NeuralAssembly:

    def __init__(self, id: str, container):
        from neurons.neuro_container import NeuroContainer
        self.pattern: str = None
        self.id = id
        self.firing = False
        self.fired = False
        self.container: NeuroContainer = container
        self.perceptual = False
        self.is_link = False
        self.is_combined = False
        self.is_joint = False
        self.doped = False
        self.firing_ticks = []
        self.firing_history = {}
        self.potential = 0
        self.threshold = 2
        self.capacity = 0
        self.formed_at = 0
        self.last_fired_at = 0
        self.hierarchy_level = 0
        self.contributors = []
        self.fired_contributors = []
        self.area: NeuralArea = None

    @property
    def is_visual(self):
        return self.pattern.startswith('v:') and ('+' not in self.pattern)

    @property
    def cleaned_pattern(self):
        if ':' not in self.pattern:
            return self.pattern
        last_colon_position = self.pattern[::-1].index(':')
        return self.pattern[len(self.pattern) - last_colon_position:].strip()

    def update(self):
        self.fired = False

        if self.potential >= self.threshold or self.container.current_tick in self.firing_ticks:
            self.firing = True

        if self.firing:
            self.last_fired_at = self.container.current_tick
            self.capacity += 1
            if self.capacity > HyperParameters.max_capacity:
                self.capacity = HyperParameters.max_capacity
            self.fired = True
            self.firing = False
            connections = self.container.get_assembly_outgoing_connections(na=self)
            for conn in connections:
                conn.pulsing = True
            self.firing_history[self.container.current_tick] = list(self.fired_contributors)
        else:
            self.fired_contributors.clear()
        self.potential = 0

    def fill_contributors(self, nas: List):
        self.contributors.clear()
        for na in nas:
            self.contributors.append(na)
        effective_contributors = []
        for na in self.contributors:
            if na.is_link and na.contributors[0] in self.contributors:
                continue
            effective_contributors.append(na)
        if len(effective_contributors) > 2:
            self.threshold = 3

    def _repr(self):
        return f'"{self.pattern}" id: {self.id}'

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()