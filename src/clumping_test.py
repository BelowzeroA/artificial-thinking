from neurons.clumped_layer import ClumpLayer
from neurons.layer import Layer
from neurons.network import Network
from neurons.neuro_container import NeuroContainer


def main():
    container = NeuroContainer()
    input_layer = Layer(container=container)
    input_layer.allocate_neurons()
    input_layer.fire_random_pattern(28)

    troubled_neuron = container.get_neuron_by_id('27')
    #troubled_neuron.potential = 1

    clump_layer = ClumpLayer(container=container)
    clump_layer.allocate_clumps()
    clump_layer.connect_to_layer(input_layer)

    network = Network(container=container)
    network.run(max_ticks=15)


if __name__ == '__main__':
    main()