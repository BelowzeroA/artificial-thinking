import random


# random.seed(43)
import math

from clusters.circuit import Circuit


class Node:

    def __init__(self, nid, pattern, container, is_sequence=False, abstract=False):
        self.pattern = pattern
        self.nid = nid
        self.container = container
        self.abstract = abstract
        self.is_sequence = is_sequence
        self.potential = 0
        self.threshold = 1
        self.fired = False
        self.firing = False
        self.is_episode = False
        self.input_pattern = set()
        self.input_nodes = set()
        self.output = []
        self.firing_history = []
        self.firing_energy = 0
        self.remembered_patterns = []
        self.firing_pathways = []
        self.causal_connections = []
        self.circuits = []
        self.prev_input_nodes = []


    def update(self, current_tick):
        if self.container.reinforcement_mode:
            self.update_reinforcement_mode(current_tick)
        elif self.container.consolidation_mode:
            if self.is_synthesizer():
                return
            self.update_consolidation_mode()
        elif self.container.urge_mode:
            self.update_urge_mode()
        else:
            if self.is_synthesizer():
                return
            self.update_learning_mode()


    def update_learning_mode(self):
        self.fired = False
        if self.potential >= self.threshold:
            self.firing = True

        if self.firing:
            self.fired = True
            self.firing = False
            out_synapses = self.container.get_outgoing_connections(self)
            for connection in out_synapses:
                if self._should_convey_signal(connection):
                    connection.pulsing = True
        self.potential = 0


    def _should_convey_signal(self, connection):
        return True
        if self.is_auditory() or self.is_visual():
            return True
        return False


    def update_reinforcement_mode(self, current_tick):
        likelihood = self._get_firing_likelihood_reinforcement_mode()
        self._update_circuits()
        if self.firing_energy == 0:
            if likelihood > 0:
                patterns = [ptrn for ptrn in self.remembered_patterns if self._input_patterns_match(ptrn['inputs'], self.input_nodes)]
                if patterns:
                    self._process_update_with_patterns(patterns, likelihood, current_tick)
                    self.potential = 0
                    return
            self.potential = 0
            margin = int(100 * likelihood)
            rand_val = random.randint(1, 100)
            if rand_val > margin:
                return
            self.firing_energy = random.choice([1, 1, 2, 2, 3])
            self.prev_input_nodes = list(self.input_nodes)

        self._on_fire_common_reinforcement_mode(current_tick)


    def _process_update_with_patterns(self, patterns, likelihood, current_tick):
        for pattern in patterns:
            circuit = self.get_circuit(self.input_nodes, pattern['output'])
            if circuit and circuit.fired:
                circuit.fired = False
                self.firing_history.append(
                    {'tick': current_tick, 'energy': circuit.firing_energy, 'output': circuit.output,
                     'input': self.input_nodes})
                continue

            coefficient = math.sqrt(pattern['rate'])
            margin = int(100 * likelihood * coefficient)
            rand_val = random.randint(1, 100)
            if rand_val > margin:
                continue
            connection = self.container.get_connection(source=self, target=pattern['output'])
            if connection:
                opposite = connection.get_opposite_connection()
                if not opposite or not opposite.pulsed:
                    connection.pulsing = True
            self.firing = True
            self.fired = True
            self.firing_history.append(
                {'tick': current_tick, 'energy': self.firing_energy, 'output': [connection], 'input': self.input_nodes})


    def _update_circuits(self):
        for circuit in self.circuits:
            circuit.update()


    def _on_fire_common_reinforcement_mode(self, current_tick):
        self.firing_energy -= 1
        self.firing_energy = max(0, self.firing_energy)
        self.firing = True
        self.fired = True
        if len(self.output) > 0:
            outputs = self._get_pulsing_outputs()
            for conn in outputs:
                opposite = conn.get_opposite_connection()
                if not opposite or not opposite.pulsed:
                    conn.pulsing = True
        if not self.is_perceptual():
            self._create_circuits(outputs)
        self.firing_history.append(
            {'tick': current_tick, 'energy': self.firing_energy, 'output': outputs, 'input': self.input_nodes})


    def _create_circuits(self, outputs):
        for output in outputs:
            pattern = self._make_pattern_for_circuit(output.target)
            circuit = self._get_circuit_by_pattern(pattern)
            if not circuit:
                circuit = Circuit(pattern=pattern, node=self)
                circuit.firing_energy = self.firing_energy
                circuit.output = output.target
                self.circuits.append(circuit)


    @staticmethod
    def _input_patterns_match(inp1, inp2):
        intersection = set(inp1) & set(inp2)
        return len(intersection) == len(inp1) and len(intersection) == len(inp2)


    def update_urge_mode(self):
        if self.is_special() and self.potential > 0:
            connections = self.container.get_outgoing_connections(self)
            for connection in connections:
                connection.pulsing = True
        else:
            pathways = self._get_matching_pathway()
            for pathway in pathways:
                self.firing = True
                self.fired = True
                connection = self.container.get_connection(source=self, target=pathway['output'])
                connection.pulsing = True
            self.potential = 0


    def _get_circuit_by_pattern(self, pattern):
        circuits = [c for c in self.circuits if c.pattern == pattern]
        if circuits:
            return circuits[0]
        return None


    def get_circuit(self, inputs, output):
        pattern = self.make_pattern_for_circuit(inputs, output)
        return self._get_circuit_by_pattern(pattern)


    def _get_matching_pathway(self):
        matched_pathways = []
        for pathway in self.firing_pathways:
            pathway_size = len(pathway['inputs'])
            intersection = [node for node in pathway['inputs'] if node in self.input_nodes]
            if len(intersection) == pathway_size:
                matched_pathways.append(pathway)
        return matched_pathways


    def _get_pulsing_outputs(self):
        # return self.output
        output_size = len(self.output)
        if output_size == 1:
            return self.output
        result_set_size = int(output_size / 2) + 1
        result = set()
        while len(result) < result_set_size:
            result.add(random.choice(self.output))
        return list(result)


    def update_consolidation_mode(self):
        if not self.firing:
            likelihood = self._get_firing_likelihood()
            margin = int(100 * likelihood)
            rand_val = random.randint(1, 100)
            if rand_val > margin:
                self.potential = 0
                return
            self.firing = True
        self.fired = True
        outgoing = self.container.get_outgoing_connections(self)
        for conn in outgoing:
            conn.pulsing = True
        self.potential = 0
        self.firing = False


    def _get_firing_likelihood_reinforcement_mode(self):
        if self.is_visual() and self.potential == 1:
            return 1.0
        if self.potential == 0.0:
            return 0.0
        elif self._there_is_visual_input():
            return 1.0
        elif self.potential == 1:
            return 0.05
        elif self.potential == 2:
            return 0.8
        else:
            return 1.0


    def _there_is_visual_input(self):
        visual_node = self.container.get_node_by_pattern('v:' + self.pattern)
        if not visual_node:
            return False
        return visual_node in self.input_nodes


    def _get_firing_likelihood(self):
        if self.potential == 0.0:
            return 0.0
        elif self.potential == 1:
            return 0.3
        elif self.potential == 2:
            return 0.8
        else:
            return 1.0


    def receive_spike(self, connection):
        self.input_pattern.add(connection)
        self.input_nodes.add(connection.source.nid)


    def is_synthesizer(self):
        return self.pattern.startswith('synth:')


    def fire(self):
        self.potential = 1


    def fire_output(self):
        if len(self.output) == 0:
            raise BaseException('No outputs for node ' + self.pattern)
        self.potential = 1
        for connection in self.output:
            connection.pulsing = True


    def set_reward(self, target_node):
        if self.is_visual() or self.is_auditory():
            return
        last_shot = self.firing_history[len(self.firing_history) - 1]
        for shot in self.firing_history:
            self._append_to_remembered_pattern(shot, target_node)


    def _append_to_remembered_pattern(self, shot, target_node):
        target_node_name = target_node.nid if target_node else 'dummy'
        self.remembered_patterns.append((shot['tick'],
                                         self._make_input_pattern_to_store(shot['input'],
                                                                           target_node), target_node_name))

    def _make_input_pattern_to_store(self, inputs, target_node):
        # opposite_connection = self.container.get_connection(target_node, self)
        # if opposite_connection:
        return ', '.join([str(node.nid) for node in inputs if node != target_node])


    def _make_pattern_for_circuit(self, output):
        pattern = ', '.join([str(node.nid) for node in self.input_nodes])
        return '{} - {}'.format(pattern, output.nid)


    def make_pattern_for_circuit(self, input_nodes, output):
        pattern = ', '.join([str(node.nid) for node in input_nodes])
        return '{} - {}'.format(pattern, output.nid if output else '')


    def _make_input_pattern_to_store0(self, raw_pattern, target_node):
        pattern = list(raw_pattern)
        opposite_connection = self.container.get_connection(target_node, self)
        if opposite_connection:
            pattern = [item for item in raw_pattern if item != opposite_connection]
        fingerprint = set()
        for connection in pattern:
            fingerprint.update(connection.fingerprint)
        # ints = [int(item) for item in list(fingerprint)]
        ints = [int(c.source.nid) for c in pattern]
        ints.sort()
        return ' '.join([str(item) for item in ints])


    def is_auditory(self):
        return self.pattern.startswith('a:')


    def is_visual(self):
        return self.pattern.startswith('v:')


    def is_perceptual(self):
        return self.is_visual() or self.is_auditory()


    def is_entity(self):
        return ':' not in self.pattern


    def is_twin(self):
        return self.pattern.endswith('twin')


    def is_special(self):
        return ':' in self.pattern


    def _repr(self):
        if self.pattern:
            return '"{}"'.format(self.pattern)
        return '[id:{}]'.format(self.nid)


    def __repr__(self):
        return self._repr()


    def __str__(self):
        return self._repr()


    def serialize(self):
        _dict = {'id': self.nid}
        if self.is_episode:
            _dict['episode'] = True
        if self.abstract:
            _dict['abstract'] = True
        if self.pattern:
            _dict['pattern'] = self.pattern
        if self.remembered_patterns:
            self.remembered_patterns.sort(key=lambda x: x[0])
            _dict['remembered_patterns'] = self.remembered_patterns
        return _dict
