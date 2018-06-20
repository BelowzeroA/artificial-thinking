

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
        self.input = []
        self.output = []


    def update(self):
        if self._is_synthesizer():
            return
        self.fired = False
        if self.potential >= self.threshold:
            self.firing = True

        if self.firing:
            self.fired = True
            self.firing = False
            out_synapses = self.container.get_outgoing_connections(self)
            for synapse in out_synapses:
                synapse.pulsing = True
        self.potential = 0


    def _is_synthesizer(self):
        return self.pattern.startswith('synth:')


    def fire(self):
        self.potential = 1


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
        if self.pattern:
            _dict['pattern'] = self.pattern
        return _dict
