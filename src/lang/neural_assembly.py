from typing import List

from lang.hyperparameters import HyperParameters


class NeuralAssembly:
    """
    Neural assembly is a stable activity pattern belonging to a certain area
    """
    def __init__(self, id: str, container):
        from neurons.neuro_container import NeuroContainer
        self.pattern: str = None
        # self.phonetic_pattern: str = None
        self.id = id
        self.firing = False
        self.fired = False
        self.container: NeuroContainer = container
        self.perceptual = False
        self.is_combined = False
        self.is_joint = False
        self.is_tone = False
        self.doped = False
        self.firing_ticks = []
        self.firing_history = {}
        self.potential = 0
        self.threshold = 2
        # self.capacity = 0
        self.formed_at = 0
        self.last_fired_at = 0
        self.hierarchy_level = 0
        self.firing_count = 1
        self.contributors = []
        self.fired_contributors: List[NeuralAssembly] = []
        self._area: 'NeuralArea' = None
        self.is_winner = False # for Winner Takes It All Strategy areas
        self.source_assemblies = []
        self.source_area = None # for tone-bases assemblies
        self.activated = False

    @property
    def area(self):
        """
        Area this NA belongs to
        :return:
        """
        return self._area

    @area.setter
    def area(self, val):
        if self._area and self._area != val:
            raise Exception(f'NeuralAssembly.set_area(): The area of {self} is already set')
        self._area = val
        msg_data = {
            'assembly': self,
            'area': val
        }
        self.container.agent.queue_message('assembly_attached_to_area', msg_data)

    @property
    def is_visual(self):
        return self.pattern.startswith('v:') and ('+' not in self.pattern)

    @property
    def cleaned_pattern(self):
        if ':' not in self.pattern:
            return self.pattern
        last_colon_position = self.pattern[::-1].index(':')
        return self.pattern[len(self.pattern) - last_colon_position:].strip()

    def update(self, current_tick: int):
        self.fired = False
        area = self.area
        if current_tick in area.inhibited_at_ticks:
            self.potential = 0
            return
        if area.winner_takes_it_all_strategy:
            if self.is_winner:
                self.firing = True
        else:
            if self.potential >= self.threshold or current_tick in self.firing_ticks:
                self.firing = area.allow_firing(self)

        if self.firing:
            self.last_fired_at = current_tick
            self.fired = True
            self.firing = False
            connections = self.container.get_assembly_outgoing_connections(na=self)
            for conn in connections:
                conn.pulsing = True
            self.firing_history[self.container.current_tick] = list(self.fired_contributors)
            area.on_fire(self)
        # else:
        self.fired_contributors.clear()
        self.potential = 0
        self.is_winner = False

    def on_doped(self, current_tick: int):
        """
        Invoked whenever dopamine reaches the assembly
        :return:
        """
        self.doped = True
        fired_contributors = self.fired_contributors
        if not fired_contributors:
            # it might be invoked from another DOPEd assembly
            # take fired contributors from the history then
            fired_contributors = self.firing_history[self.last_fired_at]
        for na in fired_contributors:
            # TODO: consider moving this hardcoded rule into a neural areas config file
            if self.area in na.area.double_activation_from:
                connection = self.container.get_connection_between_nodes(self, na)
                if not connection:
                    connection = self.container.create_connection(source=self, target=na)
                connection.multiplier = 2
            if na.area in self.area.double_activation_from:
                connection = self.container.get_connection_between_nodes(na, self)
                connection.multiplier = 2

    def is_successor_of(self, na: 'NeuralAssembly') -> bool:

        def find_in_sources(assembly: 'NeuralAssembly') -> bool:
            for a in assembly.source_assemblies:
                if a == na:
                    return True
            for a in assembly.source_assemblies:
                result = find_in_sources(a)
                if result:
                    return True
            return False

        if na == self:
            return True
        return find_in_sources(self)

    def _repr(self):
        return f'"{self.pattern}" id: {self.id}'

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()