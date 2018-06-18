import random
from collections import Counter


class Neuron:

    def __init__(self, id, container, clump=None):
        self._id = id
        self.clump = clump
        self.pattern = ''
        self.potential = 0
        self.threshold = 1
        self.firing = False
        self.fired = False
        self.container = container
        self.initial = False
        self.history = []
        # self.brain = brain


    def fire(self):
        self.potential = 1


    def update(self):
        self.fired = False
        if self.potential >= self.threshold:
            self.firing = True
            self.history.append(self.potential)

        if self.firing:
            self.fired = True
            self.firing = False
            out_synapses = self.container.get_outgoing_connections(self)
            for synapse in out_synapses:
                synapse.pulsing = True
        self.potential = 0


    def reset_history(self):
        self.history.clear()


    def update_threshold(self):
        return
        if self.history:
            self.threshold = max(self.history)


    def assign_random_threshold(self):
        if not self.initial:
            self.threshold = random.choice([1, 2])


    def update_threshold(self):
        return
        if self.history:
            self.threshold = max(self.history)
            # print('threshold:', self.threshold)
            # most_frequent = Counter(self.history).most_common(1)[0]
            # self.threshold = most_frequent[1]


    def _repr(self):
        if self.pattern:
            return '"{}"'.format(self.pattern)
        return '[id:{}]'.format(self._id)


    def __repr__(self):
        return self._repr()


    def __str__(self):
        return self._repr()


    def serialize(self):
        _dict = {'id': self._id }
        if self.pattern:
            _dict['pattern'] = self.pattern

        if self.clump:
            _dict['clump'] = self.clump._id

        if self.threshold != 0:
            _dict['threshold'] = self.threshold

        return _dict