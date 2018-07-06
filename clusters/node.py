import random

from clusters.hyper_parameters import FINGERPRINT_LENGTH

# random.seed(43)


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
        self.remembered_patterns = []
        self.causal_connections = []


    def update(self):
        if self.container.reinforcement_mode:
            self.update_reinforcement_mode()
        elif self.container.consolidation_mode:
            if self._is_synthesizer():
                return
            self.update_consolidation_mode()
        else:
            if self._is_synthesizer():
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


    def update_reinforcement_mode(self):
        likelihood = self._get_firing_likelihood()
        margin = int(100 * likelihood)
        rand_val = random.randint(1, 100)
        if rand_val > margin:
            return
        self.firing = True
        self.fired = True
        if len(self.output) > 0:
            output = random.choice(self.output)
            output.pulsing = True
            self.firing_history.append((output, list(self.input_pattern), self.input_nodes))


    def update_consolidation_mode(self):
        if not self.firing:
            likelihood = self._get_firing_likelihood_consolidation_mode()
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


    def _get_firing_likelihood(self):
        inp_len = len(self.input_pattern)
        if inp_len == 0:
            return 0.0
        incoming_connections_count = len(self.container.get_incoming_connections(self))
        if inp_len == 1:
            if incoming_connections_count == 1:
                return 0.5
            else:
                return 0.05
        if inp_len == 2:
            return 0.4
        return 1.0


    def _get_firing_likelihood_consolidation_mode(self):
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


    def _is_synthesizer(self):
        return self.pattern.startswith('synth:')


    def fire(self):
        self.potential = 1


    def fire_output(self):
        if len(self.output) == 0:
            raise BaseException('No outputs for node ' + self.pattern)
        for connection in self.output:
            connection.pulsing = True


    def set_reward(self, target_node):
        if self.is_visual() or self.is_auditory():
            return
        if self.firing_history:
            last_shot = self.firing_history[len(self.firing_history) - 1]
            self.remembered_patterns.append((self._make_input_pattern_to_store(last_shot[1], target_node), target_node.nid))
        else:
            self.remembered_patterns.append((self._make_input_pattern_to_store(self.input_pattern, target_node), 'dummy'))


    def _make_input_pattern_to_store(self, raw_pattern, target_node):
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
        _dict = {'id': self.nid }
        if self.is_episode:
            _dict['episode'] = True
        if self.pattern:
            _dict['pattern'] = self.pattern
        if self.remembered_patterns:
            _dict['remembered_patterns'] = self.remembered_patterns
        return _dict
