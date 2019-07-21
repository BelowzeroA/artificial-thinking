import random

from brain.brain import Brain
from neurons.neuron import Neuron


class Layer:

    from neurons.neuro_container import NeuroContainer

    def __init__(self, container: NeuroContainer):
        self.container = container
        self.neurons = []


    def allocate_neurons(self):
        for i in range(Brain.num_neurons_in_layer):
            neuron = Neuron(self.container.next_neuron_id(), container=self.container)
            neuron.num_firings = Brain.input_neurons_firing_count
            self.container.append_neuron(neuron)
            self.neurons.append(neuron)


    def fire_random_pattern(self, pattern_key: int):
        random.seed(pattern_key)
        neurons_copy = list(self.neurons)
        num_neurons = Brain.input_pattern_length
        neurons_to_fire = [neurons_copy.pop(random.randrange(len(neurons_copy))) for _ in range(num_neurons)]
        for neuron in neurons_to_fire:
            neuron.fire()