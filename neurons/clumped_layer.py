import random

from brain.brain import Brain
from neurons.clump import Clump
from neurons.neuro_container import NeuroContainer
from neurons.neuron import Neuron
from neurons.synapse import Synapse
from utils.misc import random_select_from_list


class ClumpLayer:

    def __init__(self, container: NeuroContainer):
        self.container = container


    def allocate_clumps(self):
        for i in range(Brain.num_clumps):
            clump_id = self.container.next_clump_id()
            clump = Clump(clump_id, pattern=clump_id, container=self.container, abstract=False)
            clump.allocate_neurons()
            self.container.append_clump(clump)


    def connect_to_layer(self, layer):
        for target_neuron in self.container.neurons:
            if not target_neuron.clump:
                continue
            avg_num = Brain.neurons_from_layer_per_clumped_neuron
            source_neurons_count = random.randrange(avg_num - 2, avg_num + 3)
            source_neurons = random_select_from_list(layer.neurons, source_neurons_count)
            #[neurons_from_layer.pop(random.randrange(len(neurons_from_layer))) for _ in range(source_neurons_count)]
            for source_neuron in source_neurons:
                synapse = Synapse(source=source_neuron, target=target_neuron)
                synapse.weight = Brain.default_synapse_weight
                self.container.synapses.append(synapse)
