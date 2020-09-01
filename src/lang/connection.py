from lang.neural_assembly import NeuralAssembly


class Connection:

    def __init__(self, container, source: NeuralAssembly, target: NeuralAssembly):
        self.source = source
        self.target = target
        self.container = container
        self.pulsing = False
        self.pulsed = False
        self.weight = 1
        self.multiplier = 1
        self.gate_cached = False
        self.gate = None

    def get_opposite_connection(self):
        return self.container.get_connection(source=self.target, target=self.source)

    def _get_gate(self):
        if self.gate_cached:
            return self.gate
        self.gate = self.container.get_neural_gate(self.source.area, self.target.area)
        self.gate_cached = True
        return self.gate

    def update(self):
        self.pulsed = False
        if self.pulsing:
            gate = self._get_gate()
            if gate is None or gate.is_open:
                self.target.potential += self.multiplier
                self.target.fired_contributors.append(self.source)
            self.pulsing = False
            self.pulsed = True

    def serialize(self):
        _dict = {
            'source': self.source.id,
            'target': self.target.id
        }
        return _dict

    def _repr(self):
        return '[{}] - [{}]'.format(self.source.pattern, self.target.pattern)

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()