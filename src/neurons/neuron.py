import random
from typing import List
from vision.common import FiringHistory


class Neuron:

    def __init__(self, id, container, clump=None):
        from neurons.synapse import Synapse
        self._id = id
        self.clump = clump
        self.pattern = ''
        self.potential = 0
        self.threshold = 1
        self.firing = False
        self.fired = False
        self.container = container
        self.initial = False
        self.inhibitory = False
        self.on_negative_reward = False
        self.num_firings = 1
        self.current_firing_counter = 0
        self.history: List[FiringHistory] = []
        self.incoming_connections: List[Synapse] = []
        self.outgoing_connections: List[Synapse] = []


    def fire(self):
        self.potential = 1


    def update(self):
        self.fired = False

        if not self.firing and self.current_firing_counter:
            self.firing = True

        # Check if the network is in GABA Release state
        can_be_fired = not self.on_negative_reward
        if self.container.network.gaba_release:
            can_be_fired = True

        if self.potential >= self.threshold:# and can_be_fired:
            self.firing = True
            self._record_history_frame()
            self.current_firing_counter = self.num_firings

        if self.firing:
            if self.clump:
                self.clump.on_neuron_firing(self)
            self.fired = True
            self.firing = False
            for synapse in self.outgoing_connections:
                synapse.pulsing = True
            if self.current_firing_counter:
                self.current_firing_counter -= 1
        self.potential = 0


    def _record_history_frame(self):
        external_excitation = []
        if self.clump:
            for conn in self.incoming_connections:
                if conn.source.clump != self.clump and conn.source.fired:
                    external_excitation.append(conn.source._id)

        self.history.append(FiringHistory(
            tick=self.container.current_tick,
            potential=self.potential,
            external_excitation=external_excitation
        ))


    def _fired_at_tick(self, tick):
        return any([h for h in self.history if h.tick == tick])


    def update_connectome_cache(self):
        """
        If the neuron just fired update it's incoming weights
        :return:
        """
        self.incoming_connections = self.container.get_incoming_connections(self)
        self.outgoing_connections = self.container.get_outgoing_connections(self)


    def update_weights(self):
        """
        Update neuron's incoming weights
        :return:
        """
        previous_tick = self.container.current_tick - 1
        if self.fired:
            for synapse in self.incoming_connections:
                if synapse.source._fired_at_tick(previous_tick):
                    synapse.upgrade_weight()
                else:
                    synapse.downgrade_weight(keep_max_value=False)
        else:
            for synapse in self.incoming_connections:
                if synapse.source._fired_at_tick(previous_tick):
                    synapse.downgrade_weight(keep_max_value=True)


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