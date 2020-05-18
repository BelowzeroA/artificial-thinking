
class Brain:

    # model hyperparameters
    num_neurons_in_clump = 10
    clump_inner_connectivity_density = 0.5
    clump_neuron_threshold = 4
    clump_output_neuron_threshold = 8
    default_synapse_weight = 0.58
    num_neurons_in_layer = 100
    input_pattern_length = 20
    num_clumps = 100
    input_neurons_firing_count = 20
    neurons_from_layer_per_clumped_neuron = 10

    def __init__(self):
        pass