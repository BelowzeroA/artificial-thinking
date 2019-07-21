import random

from typing import List

from brain.brain import Brain
from neurons.clump import Clump
from neurons.neuro_container import NeuroContainer
from neurons.neuron import Neuron
from neurons.synapse import Synapse
from utils.misc import random_select_from_list
from vision.parameters import SabParameters, HyperParameters
from vision.self_sustained_block import SelfSustainedActivityBlock


class SabLayer:
    """
    Layer of self-sustained activity blocks
    """
    def __init__(self, container: NeuroContainer, num_units: int, sab_params: SabParameters, layer_id, parent_layer=None):
        self.container = container
        self.units: List[SelfSustainedActivityBlock] = []
        self.num_units = num_units
        self.layer_id = layer_id
        self.parent_layer = parent_layer
        self.sab_params = sab_params
        self.firing_sabs = {}
        self.is_output = False


    def allocate(self):
        for i in range(self.num_units):
            layer = self.parent_layer if self.parent_layer else self
            sab = self.container.create_sab(layer=layer, params=self.sab_params)
            sab.allocate()
            self.units.append(sab)
        self._allocate_inhibitory_synapses()


    def _allocate_inhibitory_synapses(self):
        for source_sab in self.units:
            for target_sab in self.units:
                if target_sab != source_sab:
                    self._make_inhibitory_synapses_between_sabs(source=source_sab, target=target_sab)


    def _make_inhibitory_synapses_between_sabs(self, source: SelfSustainedActivityBlock, target: SelfSustainedActivityBlock):
        target_neurons = list(target.receptive_neurons)
        target_neurons.extend(target.output_neurons)
        for target_neuron in target_neurons:
            for source_neuron in source.inhibitory_neurons:
                synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
                synapse.fixed = True
                synapse.weight = HyperParameters.inhibitory_synapse_weight


    def get_output_neurons(self):
        neurons = []
        for unit in self.units:
            neurons.extend(unit.output_neurons)
        return neurons


    def get_feedforward_inhibitory_neurons(self):
        neurons = []
        for unit in self.units:
            neurons.extend(unit.feedforward_inhibitory_neurons)
        return neurons


    def get_input_neurons(self):
        neurons = []
        for unit in self.units:
            neurons.extend(unit.receptive_neurons)
        return neurons


    def connect_to(self, layer, connection_density: int):
        """
        Build synaptic connections to the previous layer
        :param layer:
        :return:
        """
        source_sabs = layer.get_all_sabs()
        receptive_neurons = layer.get_input_neurons()
        ff_inhibitory_neurons = layer.get_feedforward_inhibitory_neurons()
        for unit in self.units:
            # feedforward connections
            # from feedforward inhibitory to receptive
            unit.build_synapses_from_ff_inhibitory_neurons(ff_inhibitory_neurons)
            # from receptive to receptive
            for source_sab in source_sabs:
                unit.build_synapses_from_source_sab(source_sab, connection_density)
            # feedback connections
            # unit.build_synapses_to_target_neurons(receptive_neurons)



    def on_sab_firing(self, sab):
        if not self.sab_belongs_to(sab):
            return

        if self.is_output:
            # if this SAB is in the output layer, check if it's the right SAB that is firing
            # If the wrong SAB is on fire, turn on the GABA release mechanism
            self._check_on_output_layer(sab)

        if sab._id in self.firing_sabs:
            self.firing_sabs[sab._id] += 1
        else:
            self.firing_sabs[sab._id] = 1

    def _check_on_output_layer(self, sab):
        current_label_sab = self.container.get_current_label_sab()
        if sab.label:
            if sab.label != self.container.current_label:
                self.gaba_release()
        else:
            sab.label = self.container.current_label


    def gaba_release(self):
        return
        network = self.container.network
        if not network.gaba_release:
            network.gaba_release = True


    def sab_belongs_to(self, sab):
        return sab in self.units


    def get_winning_sab(self):
        items = list(self.firing_sabs.items())
        if not items:
            return None
        items.sort(key=lambda x: x[1], reverse=True)
        winning_sab_id = items[0][0]
        return [sab for sab in self.units if sab._id == winning_sab_id][0]

