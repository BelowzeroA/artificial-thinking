import random


class Synapse:

    def __init__(self, source, target, inhibitory=False):
        self.source = source
        self.target = target
        self.pulsing = False
        self.weight = 0
        self.inhibitory = inhibitory
        self.history = []


    def update(self):
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
        sign = -1 if self.inhibitory else 1
        self.target.potential += sign


    def reset_history(self):
        self.history.clear()


    def update_weight(self, learning_rate):
        summary = sum(self.history)
        if summary > 0:
            self.weight += learning_rate
        elif summary < 0:
            self.weight -= learning_rate
        self.weight = min(1, max(0, self.weight))


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