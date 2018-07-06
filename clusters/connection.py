import random

from clusters.hyper_parameters import FINGERPRINT_LENGTH, INPUT_GATE_SIZE


class Connection:

    def __init__(self, container, source, target):
        self.source = source
        self.target = target
        self.container = container
        self.fingerprint = []
        self.source_gate = 0
        self.generate_fingerprint()
        self.pulsing = False
        self.pulsed = False
        self.weight = 0


    def generate_fingerprint(self):
        fp = set()
        while len(fp) < FINGERPRINT_LENGTH:
            fp.add(random.randint(1, INPUT_GATE_SIZE))
        fp = list(fp)
        fp.sort()
        self.fingerprint = fp


    def update(self):
        if self.pulsing:
            opposite = self.container.get_connection(source=self.target, target=self.source)
            opposite_pulsed = opposite and opposite.pulsed
            self.pulsed = True
            if self.container.reinforcement_mode:
                if not opposite_pulsed:
                    self.target.receive_spike(self)
            else:
                if not opposite_pulsed:
                    self.target.potential += 1
                    self.target.input_nodes.add(self.source)
                    self.target.causal_connections.append(self)
            self.pulsing = False


    def serialize(self):
        _dict = {
            'source': self.source.nid,
            'target': self.target.nid,
            'fingerprint': ' '.join([str(port) for port in self.fingerprint])
        }
        return _dict


    def _repr(self):
        return '"{}" - "{}"'.format(self.source.pattern, self.target.pattern)


    def __repr__(self):
        return self._repr()


    def __str__(self):
        return self._repr()