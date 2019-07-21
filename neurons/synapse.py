import random
from neurons.neuron import Neuron
from vision.parameters import HyperParameters

LEARNING_RATE = 0.05


class Synapse:

    def __init__(self, source: Neuron, target: Neuron, inhibitory=False):
        self.source = source
        self.target = target
        self.pulsing = False
        self.pulsed = False
        self.weight = 1
        self.inhibitory = inhibitory
        self.history = []
        self.fixed = inhibitory


    def update(self):
        self.pulsed = False
        if self.pulsing:
            if self.weight == 0.0:
                return
            margin = int(100 * self.weight)
            rand_val = random.randint(1, 100)
            if rand_val <= margin:
                self._release()
                self.history.append(1)
            else:
                self.history.append(-1)
            self.pulsing = False


    def _release(self):
        val = -HyperParameters.inhibitory_synapse_potential if self.inhibitory else 1
        self.target.potential += val
        self.pulsed = True


    def reset_history(self):
        self.history.clear()


    def update_weight(self, learning_rate):
        summary = sum(self.history)
        if summary > 0:
            self.weight += learning_rate
        elif summary < 0:
            self.weight -= learning_rate
        self.weight = min(1, max(0, self.weight))


    def upgrade_weight(self):
        network = self.source.container.network
        if self.source.on_negative_reward:
            if network.gaba_release:
                self.weight += LEARNING_RATE
            else:
                self.weight -= LEARNING_RATE
            self._crop_weight(min_margin=HyperParameters.feedforward_inhibitory_synapse_weight, max_margin=1)
        if self.fixed:
            return
        self.weight += LEARNING_RATE
        if self.weight > 1:
            self.weight = 1


    def _crop_weight(self, min_margin, max_margin):
        if self.weight < min_margin:
            self.weight = min_margin
        if self.weight > max_margin:
            self.weight = max_margin


    def downgrade_weight(self, keep_max_value=False):
        if self.fixed:
            return
        if keep_max_value and self.weight > 0.9:
            return
        self.weight -= LEARNING_RATE / 2
        self._crop_weight(min_margin=HyperParameters.min_synapse_weight, max_margin=1)


    def serialize(self):
        _dict = {
            'source': self.source._id,
            'target': self.target._id,
            'weight': self.weight,
            'inhibitory': self.inhibitory
        }
        return _dict

    def _repr(self):
        return '[{}-{}]'.format(self.source._id, self.target._id)

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()