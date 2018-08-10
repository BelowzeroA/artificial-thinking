import random


# random.seed(43)
import math

from clusters.circuit import Circuit


class Node:
    """
    Represents Ensemble entity, a basic brain macro-structure
    Consists of neural circuits
    """
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
        self.causal_connections = []
        self.firing_energy = 0
        self.remembered_patterns = []
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
            self.update_urge_mode(current_tick)
        else:
            if self.is_synthesizer():
                return
            self.update_learning_mode()


    def append_circuit(self, circuit):
        if circuit not in self.circuits:
            self.circuits.append(circuit)


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
        circuits = self._ensure_circuits()
        fired = False
        for circuit in circuits:
            circuit.update(current_tick)
            fired = circuit.fired or fired
        self.potential = 0
        if fired:
            self.firing = True
            self.fired = True
        self.input_nodes.clear()


    def _ensure_circuits(self):
        result = []
        if len(self.input_nodes) > 0:
            outgoing = self.container.get_outgoing_connections(self)
            for conn in outgoing:
                circuit = self._ensure_circuit(conn.target)
                if circuit:
                    result.append(circuit)
        for circuit in self.circuits:
            if circuit.firing_energy > 0 and circuit not in result:
                result.append(circuit)
        return result


    def _ensure_circuit(self, output_node):
        circuits = [c for c in self.circuits if c.matches_input(self.input_nodes) and c.output_node == output_node]
        if circuits:
            return circuits[0]
        if output_node in self.input_nodes:
            return None
        circuit = Circuit(node=self, output_node=output_node)
        self.append_circuit(circuit)
        return circuit


    def get_firing_history(self):
        result = []
        for circuit in self.circuits:
            result.extend(circuit.firing_history)
        return result


    @staticmethod
    def _input_patterns_match(inp1, inp2):
        intersection = set(inp1) & set(inp2)
        return len(intersection) == len(inp1) and len(intersection) == len(inp2)


    def update_urge_mode(self, current_tick):
        if self.is_perceptual() and self.potential > 0:
            connections = self.container.get_outgoing_connections(self)
            for connection in connections:
                connection.pulsing = True
        else:
            fired = False
            circuits = [c for c in self.circuits if c.matches_input(self.input_nodes)]
            for circuit in circuits:
                circuit.update(current_tick)
                fired = circuit.fired or fired
            self.potential = 0
            if fired:
                self.firing = True
                self.fired = True


    def get_circuit_by_pattern(self, pattern):
        circuits = [c for c in self.circuits if c.pattern == pattern]
        if circuits:
            return circuits[0]
        return None


    def get_circuit_by_input_pattern(self, input_pattern):
        circuits = [c for c in self.circuits if c.input_pattern == input_pattern]
        if circuits:
            return circuits[0]
        return None


    def get_circuit(self, inputs, output):
        pattern = Circuit.make_pattern(inputs, output)
        return self.get_circuit_by_pattern(pattern)


    def clear_firing_history(self):
        for circuit in self.circuits:
            circuit.firing_history.clear()
            circuit.firing_energy = 0


    def _get_pulsing_outputs(self):
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


    def there_is_visual_input(self):
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


    def fire(self):
        self.potential = 1


    def fire_output(self):
        if len(self.output) == 0:
            raise BaseException('No outputs for node ' + self.pattern)
        self.potential = 1
        for connection in self.output:
            connection.pulsing = True


    def _make_input_pattern_to_store(self, inputs, target_node):
        return ', '.join([str(node.nid) for node in inputs if node != target_node])


    def _make_pattern_for_circuit(self, output):
        pattern = ', '.join([str(node.nid) for node in self.input_nodes])
        return '{} - {}'.format(pattern, output.nid)


    def is_auditory(self):
        return self.pattern.startswith('a:')


    def is_visual(self):
        return self.pattern.startswith('v:')


    def is_synthesizer(self):
        return self.pattern.startswith('synth:')


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
        return _dict
