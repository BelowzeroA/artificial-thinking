import math
import random


class Circuit:

    def __init__(self, node, output_node):
        self.node = node
        self.container = node.container
        self.input_nodes = list(node.input_nodes)
        self.input_pattern = self._get_input_pattern(self.input_nodes)
        self.output_node = output_node
        self.__firing_energy = 0
        self.pattern_firing_energy = 0
        self.fixed_firing_energy = 0
        self.weight = 1
        self.fired = False
        self.firing_history = []
        self.pattern = self._make_pattern()


    @property
    def firing_energy(self):
        return self.__firing_energy


    @firing_energy.setter
    def firing_energy(self, fe):
        self.__firing_energy = fe


    def matches_input(self, input_nodes):
        pattern = self._get_input_pattern(input_nodes)
        return pattern == self.input_pattern


    @staticmethod
    def _get_input_pattern(input_nodes):
        ids = [int(node.nid) for node in input_nodes]
        ids.sort()
        return ', '.join([str(id) for id in ids])


    def _make_pattern(self):
        return '{} - {}'.format(self.input_pattern, self.output_node.nid)


    def update(self, current_tick):
        self.fired = False
        if self.firing_energy == 0:
            likelihood = self._get_firing_likelihood()
            margin = int(100 * likelihood)
            rand_val = random.randint(1, 100)
            if rand_val > margin:
                return
            fe_distribution = self._get_initial_firing_energy_distribution()
            self.pattern_firing_energy = random.choice(fe_distribution)
            self.firing_energy = self.pattern_firing_energy
            self._on_fire(current_tick)
        else:
            self._on_fire(current_tick, append_to_history=False)


    def _get_initial_firing_energy_distribution(self):
        if self.fixed_firing_energy == 0:
            return [1, 1, 2, 2, 3, 3]
        distribution = []
        sample = 2
        for i in range(1, 4):
            if i == self.fixed_firing_energy:
                distribution.extend([i] * sample * 3)
            else:
                distribution.extend([i] * sample)
        return distribution


    def _on_fire(self, current_tick, append_to_history=True):
        self.firing_energy -= 1
        self.firing_energy = max(0, self.firing_energy)
        connection = self.container.get_connection(source=self.node, target=self.output_node)
        if connection:
            self.fired = True
            opposite = connection.get_opposite_connection()
            if not opposite or not opposite.pulsed:
                connection.pulsing = True
                if append_to_history:
                    self.firing_history.append(
                    {'tick': current_tick, 'energy': self.pattern_firing_energy, 'output': self.output_node, 'input': self.input_nodes})


    def _get_firing_likelihood(self):
        likelihood = 0
        if self.node.is_visual() and self.node.potential == 1:
            likelihood = 1.0
        elif self.node.potential == 0.0:
            likelihood = 0.0
        elif self.node.there_is_visual_input():
            likelihood = 1.0
        elif self.node.potential == 1:
            likelihood = 0.05
        elif self.node.potential == 2:
            likelihood = 0.8
        else:
            likelihood = 1.0
        return likelihood * self.weight


    def _repr(self):
        return '{} ({})'.format(self.pattern, self.pattern_firing_energy)


    def __repr__(self):
        return self._repr()


    def __str__(self):
        return self._repr()