from lang.neural_area import NeuralArea
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
        self.delayed_activation_at = 0

    def get_opposite_connection(self):
        return self.container.get_connection(source=self.target, target=self.source)

    def _get_gate(self):
        if self.gate_cached:
            return self.gate
        if issubclass(type(self.source), NeuralArea):
            source_area = self.source
        else:
            source_area = self.source.area
        self.gate = self.container.get_neural_gate(source_area, self.target.area)
        self.gate_cached = True
        return self.gate

    def update(self):
        self.pulsed = False
        current_tick = self.target.area.agent.environment.current_tick
        if not self.pulsing and self.delayed_activation_at == current_tick:
            # disabled until the logic of delayed activation is discovered
            pass
            # self.signal_target()
        if self.pulsing:
            gate = self._get_gate()
            if gate is None or gate.is_open(self):
                self.signal_target(gate)
            elif gate is not None:
                self.delayed_activation_at = current_tick + 4
            self.pulsed = True
        self.pulsing = False

    def signal_target(self, gate):
        self.target.potential += self.multiplier
        if self.multiplier > 0:
            self.target.fired_contributors.append(self.source)
            if gate:
                gate.on_assembly_pass(self.target)

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