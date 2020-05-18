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

    def get_opposite_connection(self):
        return self.container.get_connection(source=self.target, target=self.source)

    def update(self):
        self.pulsed = False
        if self.pulsing:
            self.target.potential += self.multiplier
            self.target.fired_contributors.append(self.source)
            # opposite = self.container.get_connection(source=self.target, target=self.source)
            # opposite_pulsed = opposite and opposite.pulsed
            # self.pulsed = True
            # if not opposite_pulsed:
            #     self.target.potential += 1
            #     self.target.input_nodes.add(self.source)
            #     self.target.causal_connections.append(self)
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