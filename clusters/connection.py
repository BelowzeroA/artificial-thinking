import random

from clusters.hyper_parameters import FINGERPRINT_LENGTH, INPUT_GATE_SIZE


class Connection:

    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.fingerprint = []
        self.source_gate = 0
        self.generate_fingerprint()
        self.pulsing = False
        self.weight = 0


    def generate_fingerprint(self):
        fp = set()
        while len(fp) < FINGERPRINT_LENGTH:
            fp.add(random.randint(1, INPUT_GATE_SIZE))
        self.fingerprint = list(fp)


    def update(self):
        if self.pulsing:
            self.target.potential += 1
            self.pulsing = False


    def serialize(self):
        _dict = {
            'source': self.source.nid,
            'target': self.target.nid,
            'fingerprint': ' '.join([str(port) for port in self.fingerprint])
        }
        return _dict