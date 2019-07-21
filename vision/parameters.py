

class HyperParameters:
    sab_num_receptive_neurons = 10
    multi_oriented_sab_num_receptive_neurons = 320
    receptive_neuron_threshold = 3
    min_synapse_weight = 0.5
    inhibitory_synapse_potential = 0.5
    inhibitory_synapse_weight = 0.95
    receptive_dendrite_threshold = 20
    neural_grid_width = 30
    neural_grid_height = 30
    gaba_release_length = 10
    feedforward_inhibitory_synapse_weight = 0.1


class SabParameters:

    def __init__(self):
        self.interconnection_density = 0.5
        self.receptive_synapse_weight = 0.6
        self.inter_synapse_weight = 0.8
        self.sustained_activity_output_threshold = 8
        self.num_sad_neurons = 2
        self.num_feedforward_inhibitory_neurons = 1
        self.feedforward_inhibitory_neuron_threshold = 8
        self.inhibitory_neurons_lowest_threshold = 5
        self.inhibitory_neurons_uppermost_threshold = 8