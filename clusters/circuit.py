import math
import random


class Circuit:
    """
    Represents a Circuit entity:
    1) Circuit is a part of a Node
    2) responsible for precise connecting of nodes: maps input nodes to an output node
    3) used in reinforcement mode and urge mode
    """
    def __init__(self, node, output_node):
        """
        :param node: a node this circuit belongs to
        :param output_node: an output node
        """
        self.node = node
        self.container = node.container
        self.input_nodes = list(node.input_nodes)
        self.input_pattern = Circuit.get_input_pattern(self.input_nodes)
        self.output_node = output_node
        self.__firing_energy = 0
        self.pattern_firing_energy = 0
        self.fixed_firing_energy = 0
        self.weight = 1
        self.fired = False
        self.firing_history = []
        self.pattern = Circuit.make_pattern(self.input_nodes, self.output_node)


    @property
    def firing_energy(self):
        """
        Current value of firing energy
        The value denotes how many ticks the circuit should fire after initial firing
        :return:
        """
        return self.__firing_energy


    @firing_energy.setter
    def firing_energy(self, fe):
        self.__firing_energy = fe


    def matches_input(self, input_nodes):
        """
        Matches input nodes against self.input_nodes
        :param input_nodes:
        :return: True if parameter matches
        """
        pattern = self.get_input_pattern(input_nodes)
        return pattern == self.input_pattern


    @staticmethod
    def get_input_pattern(input_nodes):
        """
        Constructs a string representation from the parameter
        :param input_nodes:
        :return: string like '12, 34, 54'
        """
        ids = [int(node.nid) for node in input_nodes]
        ids.sort()
        return ', '.join([str(id) for id in ids])\


    @staticmethod
    def load_from_json(node, container, entry):
        output_node = container.get_node_by_id(entry['output'])
        pattern = Circuit._make_pattern(entry['input'], output_node)
        circuit = node.get_circuit_by_pattern(pattern)
        if not circuit:
            circuit = Circuit(node, output_node)
            circuit.input_pattern = entry['input']
            circuit.fixed_firing_energy = int(entry['energy'])
            circuit.weight = entry['weight']
            circuit.pattern = circuit._make_pattern(circuit.input_pattern, circuit.output_node)
        return circuit


    @staticmethod
    def _make_pattern(input_pattern, output_node):
        """
        Constructs a circuit representation from the parameters
        :param input_nodes:
        :return: string like '12, 34, 54 - 45'
        """
        return '{} - {}'.format(input_pattern, output_node.nid if output_node else '')


    @staticmethod
    def make_pattern(input_nodes, output_node):
        """
        Constructs a circuit representation from the parameters
        :param input_nodes:
        :return: string like '12, 34, 54 - 45'
        """
        input_pattern = Circuit.get_input_pattern(input_nodes)
        return Circuit._make_pattern(input_pattern, output_node)


    def update(self, current_tick):
        """
        Updates the state of a circuit.
        It will fire or not depending on self.weight and the number of firing input nodes
        :param current_tick: current tick
        :return:
        """
        self.fired = False
        if self.firing_energy == 0:
            likelihood = self._get_firing_likelihood()
            margin = int(100 * likelihood)
            rand_val = random.randint(1, 100)
            if rand_val > margin:
                return
            if self.container.urge_mode:
                self.firing_energy = self.fixed_firing_energy
            else:
                fe_distribution = self._get_initial_firing_energy_distribution()
                self.pattern_firing_energy = random.choice(fe_distribution)
                self.firing_energy = self.pattern_firing_energy
            self._on_fire(current_tick)
        else:
            self._on_fire(current_tick, append_to_history=False)


    def _get_initial_firing_energy_distribution(self):
        """
        Returns a list of possible energy values distribution
        :return:
        """
        if self.fixed_firing_energy == 0:
            return [1, 1, 2, 2, 3, 3]
        distribution = []
        for i in range(1, 4):
            if i == self.fixed_firing_energy:
                distribution.extend([i] * 4)
            else:
                distribution.extend([i])
        return distribution


    def _on_fire(self, current_tick, append_to_history=True):
        """
        Circuit firing behavior
        Makes the corresponding output connection pulse
        :param current_tick:
        :param append_to_history:
        :return:
        """
        self.firing_energy -= 1
        self.firing_energy = max(0, self.firing_energy)
        connection = self.container.get_connection(source=self.node, target=self.output_node)
        if connection:
            was_fired = self.fired
            self.fired = True
            appended = False
            opposite = connection.get_opposite_connection()
            if not opposite or not opposite.pulsed:
                connection.pulsing = True
                if append_to_history:
                    self.firing_history.append(
                    {'tick': current_tick, 'energy': self.pattern_firing_energy, 'output': self.output_node, 'input': self.input_nodes})
                    appended = True


    def _get_firing_likelihood(self):
        """
        Returns firing likelihood depending on self.weight and the number of firing input nodes
        :return:
        """
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


    def serialize(self):
        _dict = {
            'node': self.node.nid,
            'input': self.input_pattern,
            'output': self.output_node.nid if self.output_node else '',
            'energy': self.fixed_firing_energy,
            'weight': self.weight}
        return _dict


    def _repr(self):
        return '{} ({})'.format(self.pattern, self.pattern_firing_energy)


    def __repr__(self):
        return self._repr()


    def __str__(self):
        return self._repr()