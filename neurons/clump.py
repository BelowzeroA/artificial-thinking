from brain.brain import Brain
from neurons.neuron import Neuron
from neurons.synapse import Synapse


class Clump:

    def __init__(self, id, pattern, container, abstract=False):
        self._id = id
        self.pattern = pattern
        self.abstract = abstract
        self.container = container
        self.neurons = []
        self.synapses = []


    def allocate_neurons(self):
        for i in range(Brain.num_neurons_in_clump):
            neuron = Neuron(self.container.next_neuron_id(), self)
            self.container.append_neuron(neuron)
            self.neurons.append(neuron)
        self._build_synapses()


    def _build_synapses(self):
        for neuron_source in self.neurons:
            for neuron_dest in self.neurons:
                if neuron_dest == neuron_source:
                    continue
                self._create_synapses(neuron_source, neuron_dest)


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