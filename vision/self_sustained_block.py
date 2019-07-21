from typing import List

from neurons.neuron import Neuron
from utils.misc import random_select_from_list
from vision.parameters import HyperParameters, SabParameters
from vision.receptive_layer import Orientation


class SelfSustainedActivityBlock:
    """
    Neuronal block that sustains activity inside of it
    """
    from neurons.neuro_container import NeuroContainer

    def __init__(self, id, container: NeuroContainer, layer, params: SabParameters):
        from vision.sab_combo_layer import SabComboLayer
        from neurons.neuro_container import NeuroContainer
        self._id = id
        self.container: NeuroContainer = container
        self.receptive_neurons = []
        self.output_neurons = []
        self.synapses = []
        self.concept = None
        self.layer = layer
        self.params = params
        self.inhibitory_neurons = []
        self.history = {}
        # neurons providing inhibition to downstream layers, turned on on confusion event
        self.feedforward_inhibitory_neurons = []
        self.label: str = None
        self.orientations: List[Orientation] = []
        self.connection_density: int = 0
        self.region: SabComboLayer = None


    def fire(self):
        """
        Provides externally caused "firing" state
        :return:
        """
        for neuron in self.receptive_neurons:
            neuron.potential = 10


    def allocate(self):
        num_receptive_neurons = HyperParameters.sab_num_receptive_neurons
        if len(self.orientations) > 1:
            num_receptive_neurons = HyperParameters.multi_oriented_sab_num_receptive_neurons
        for i in range(num_receptive_neurons):
            neuron = self.container.create_neuron()
            neuron.threshold = HyperParameters.receptive_neuron_threshold #len(self.orientations)
            neuron.clump = self
            self.receptive_neurons.append(neuron)

        for i in range(self.params.num_sad_neurons):
            neuron = self.container.create_neuron()
            neuron.threshold = self.params.sustained_activity_output_threshold
            neuron.clump = self
            self.output_neurons.append(neuron)

        self._allocate_inhibitory_neurons()

        self._build_synapses()


    def _allocate_inhibitory_neurons(self):
        num_neurons = 0
        # inter-sab lateral connections
        for threshold in range(self.params.inhibitory_neurons_lowest_threshold,
                               self.params.inhibitory_neurons_uppermost_threshold + 1):
            num_neurons += 1
            for _ in range(num_neurons):
                neuron = self.container.create_neuron()
                neuron.clump = self
                neuron.threshold = threshold
                neuron.inhibitory = True
                self.inhibitory_neurons.append(neuron)
        # feedforward connections
        for _ in range(self.params.num_feedforward_inhibitory_neurons):
            neuron = self.container.create_neuron()
            neuron.clump = self
            neuron.threshold = self.params.feedforward_inhibitory_neuron_threshold
            neuron.inhibitory = True
            neuron.on_negative_reward = True
            self.feedforward_inhibitory_neurons.append(neuron)


    def build_synapses_from_ff_inhibitory_neurons(self, neurons):
        """
        Builds feedforward inhibitory interlayer synapses for the forward pass
        :param neurons: Source neurons from the previous layer
        :param connection_density:
        :return:
        """
        if not neurons:
            return
        for target_neuron in self.receptive_neurons:
            for source_neuron in neurons:
                synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
                synapse.weight = HyperParameters.feedforward_inhibitory_synapse_weight
                synapse.fixed = True


    def build_synapses_from_source_neurons(self, neurons, connection_density=0):
        """
        Builds excitatory synapses for the forward pass
        :param neurons: Source neurons from the previous layer
        :param connection_density:
        :return:
        """
        if not neurons:
            return
        for target_neuron in self.receptive_neurons:
            if connection_density:
                source_neurons = random_select_from_list(neurons, connection_density)
            else:
                source_neurons = neurons
            for source_neuron in source_neurons:
                synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
                synapse.weight = self.params.receptive_synapse_weight


    def build_synapses_to_target_neurons(self, neurons, connection_density=0):
        """
        Builds synapses for teaching signal backpropagation
        :param neurons: Target neurons from previous layer
        :param connection_density:
        :return:
        """
        if not neurons:
            return
        if connection_density:
            target_neurons = random_select_from_list(neurons, connection_density)
        else:
            target_neurons = neurons
        for target_neuron in target_neurons:
            for source_neuron in self.output_neurons:
                synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
                synapse.weight = 1
                synapse.fixed = True


    def build_synapses_from_source_sab0(self, sab, connection_density):
        """
        Builds synapses for feedforward signal passage
        :param sab: Source SAB
        :param connection_density:
        :return:
        """
        source_neurons = random_select_from_list(sab.receptive_neurons, connection_density)
        target_neurons = random_select_from_list(self.receptive_neurons, connection_density)
        for source_neuron, target_neuron in zip(source_neurons, target_neurons):
            synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
            synapse.weight = self.params.receptive_synapse_weight


    def build_synapses_from_source_sab(self, sab, connection_density):
        """
        Builds synapses for feedforward signal passage
        :param sab: Source SAB
        :param connection_density:
        :return:
        """
        source_neurons = sab.output_neurons
        target_neurons = random_select_from_list(self.receptive_neurons, connection_density)
        for source_neuron, target_neuron in zip(source_neurons, target_neurons):
            synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
            synapse.weight = self.params.receptive_synapse_weight


    def _build_synapses(self):
        num_synapses = int(self.params.interconnection_density * HyperParameters.sab_num_receptive_neurons)
        for target_neuron in self.receptive_neurons:
            source_neurons = random_select_from_list(self.receptive_neurons, num_synapses)
            for source_neuron in source_neurons:
                if source_neuron != target_neuron:
                    synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
                    synapse.weight = self.params.inter_synapse_weight
                    synapse.fixed = True

        # Receptive => Output
        for source_neuron in self.receptive_neurons:
            for target_neuron in self.output_neurons:
                synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
                synapse.fixed = True

        # Receptive => intralayer inhibitory
        for source_neuron in self.receptive_neurons:
            for target_neuron in self.inhibitory_neurons:
                synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
                synapse.fixed = True

        # Receptive => Feedforward inhibitory
        for source_neuron in self.receptive_neurons:
            for target_neuron in self.feedforward_inhibitory_neurons:
                synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
                synapse.fixed = True


    def on_neuron_firing(self, neuron):
        if neuron in self.output_neurons:
            self.layer.on_sab_firing(self)
        if neuron in self.receptive_neurons:
            current_tick = self.container.current_tick
            if current_tick not in self.history:
                self.history[current_tick] = []
            self.history[current_tick].append(neuron)


    def _repr(self):
        return '[id: {} layer: {}]'.format(self._id, self.layer.layer_id)


    def __repr__(self):
        return self._repr()


    def __str__(self):
        return self._repr()