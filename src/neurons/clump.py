import random

from brain.brain import Brain
from neurons.neuron import Neuron
from neurons.synapse import Synapse
from utils.misc import random_select_from_list


class Clump:

    def __init__(self, id, pattern, container, abstract=False):
        self._id = id
        self.pattern = pattern
        self.abstract = abstract
        self.container = container
        self.neurons = []
        self.output_neuron = None
        self.synapses = []


    def allocate_neurons(self):
        for i in range(Brain.num_neurons_in_clump):
            neuron = Neuron(self.container.next_neuron_id(), self.container, clump=self)
            neuron.threshold = Brain.clump_neuron_threshold
            self.container.append_neuron(neuron)
            self.neurons.append(neuron)

        self.output_neuron = Neuron(self.container.next_neuron_id(), self.container, clump=self)
        self.output_neuron.threshold = Brain.clump_output_neuron_threshold
        self.container.append_neuron(self.output_neuron)

        self._build_synapses()


    def _build_synapses(self):
        avg_num_synapses = int(Brain.clump_inner_connectivity_density * Brain.num_neurons_in_clump)
        for target_neuron in self.neurons:
            source_neurons_count = random.randrange(avg_num_synapses - 1, avg_num_synapses + 2)
            source_neurons = random_select_from_list(self.neurons, source_neurons_count)
            for source_neuron in source_neurons:
                if source_neuron != target_neuron:
                    synapse = Synapse(source=source_neuron, target=target_neuron)
                    self.container.append_synapses([synapse])

        for source_neuron in self.neurons:
            synapse = Synapse(source=source_neuron, target=self.output_neuron)
            self.container.append_synapses([synapse])



    def _create_synapses(self, neuron1, neuron2):
        syn1 = Synapse(neuron1, neuron2)
        self.synapses.append(syn1)
        syn2 = Synapse(neuron1, neuron2, inhibitory=True)
        self.synapses.append(syn2)
        self.container.append_synapses([syn1, syn2])


    def serialize(self):
        _dict = {
            'id': self._id,
            'pattern': self.pattern,
            'abstract': self.abstract
        }
        return _dict