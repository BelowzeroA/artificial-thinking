import itertools
import random

from typing import List

from neurons.neuro_container import NeuroContainer
from vision.common import Coord
from vision.parameters import SabParameters
from vision.receptive_layer import Orientation, ReceptiveLayer
from vision.receptive_neuron import ReceptiveNeuron
from vision.sab_combo_layer import SabComboLayer
from vision.sab_layer import SabLayer
from neurons.synapse import Synapse
from utils.misc import random_select_from_list
from vision.self_sustained_block import SelfSustainedActivityBlock


class SabPoolingLayer:
    """
    Layer of self-sustained activity blocks divided into pooling regions
    """
    def __init__(self, layer_id, container: NeuroContainer, regions_shape: tuple,
                 num_sabs_per_region: int = 0, sab_params: SabParameters = None):
        self.layer_id = layer_id
        self.container = container
        self.regions: List[SabLayer] = []
        self.regions_shape = regions_shape
        self.num_sabs_per_region = num_sabs_per_region
        self.sab_params = sab_params


    def allocate(self):
        for y in range(self.regions_shape[0]):
            for x in range(self.regions_shape[1]):
                coord = Coord(x=x, y=y)
                region = SabComboLayer(
                    layer_id=self.layer_id,
                    container=self.container,
                    num_units=self.num_sabs_per_region,
                    coord=coord,
                    parent_layer=self,
                    sab_params=self.sab_params
                )
                # region.receptive_synapse_weight = self.receptive_synapse_weight
                region.allocate()
                self.regions.append(region)


    def get_output_neurons(self):
        neurons = []
        for region in self.regions:
            neurons.extend(region.get_output_neurons())
        return neurons


    def get_feedforward_inhibitory_neurons(self):
        neurons = []
        for region in self.regions:
            neurons.extend(region.get_feedforward_inhibitory_neurons())
        return neurons


    def get_input_neurons(self):
        neurons = []
        for region in self.regions:
            neurons.extend(region.get_input_neurons())
        return neurons


    def get_all_sabs(self):
        sabs = []
        for region in self.regions:
            sabs.extend(region.units)
        return sabs


    def connect_to(self, layer):
        self._connect_to_receptive_layer(layer)


    def _connect_to_receptive_layer(self, layer):
        for region in self.regions:
            self._connect_region_to_receptive_layer(region, layer)


    def _connect_region_to_receptive_layer(self, region: SabLayer, layer: ReceptiveLayer):
        covered_orientations = [Orientation.vertical, Orientation.horizontal]
        orientations = [Orientation.__dict__[key] for key in Orientation.__dict__ if not key.startswith('_')]
        combinations = list(itertools.combinations_with_replacement(covered_orientations, 2))
        num_combinations = len(combinations)

        # num_combinations_per_unit = num_combinations / region.num_units

        receptive_width = round(layer.width / self.regions_shape[1])
        receptive_height = round(layer.height / self.regions_shape[0])

        horizontal_overlap = round(receptive_width / 3)
        vertical_overlap = round(receptive_height / 3)

        left_overlap = horizontal_overlap if region.coord.x > 0 else 0
        right_overlap = horizontal_overlap if region.coord.x < self.regions_shape[1] - 1 else 0
        upper_overlap = vertical_overlap if region.coord.y > 0 else 0
        lower_overlap = vertical_overlap if region.coord.y < self.regions_shape[0] - 1 else 0

        left_boundary = region.coord.x * receptive_width - left_overlap
        right_boundary = (region.coord.x + 1) * receptive_width + right_overlap
        upper_boundary = region.coord.y * receptive_height - upper_overlap
        lower_boundary = (region.coord.y + 1) * receptive_height + lower_overlap

        source_neurons = []
        for neuron in layer.neurons:
            if neuron.coord.x in range(left_boundary, right_boundary) and \
                    neuron.coord.y in range(upper_boundary, lower_boundary):
                source_neurons.append(neuron)

        for combination in combinations:
            combination_list = [combination[0], combination[1]]

        # feedforward excitatory connections
        # for unit, combination in zip(region.units, combinations):
        #     # combination = random.choice(combinations)
        #     combination_list = [combination[0], combination[1]]
        #     selected_nurons = [neuron for neuron in source_neurons if neuron.orientation in combination_list]
        #     unit.build_synapses_from_source_neurons(selected_nurons, 10)

        # feedforward excitatory connections
        for unit in region.units:
            if len(unit.orientations) > 1:
                self._connect_unit_to_multiple_orientations(unit, source_neurons)
            else:
                self._connect_unit_to_single_orientation(unit, source_neurons)


    def _connect_unit_to_multiple_orientations(self, unit: SelfSustainedActivityBlock, source_neurons: List[ReceptiveNeuron]):
        oriented_source_neurons = {}
        for orientation in unit.orientations:
            oriented_source_neurons[orientation] = [n for n in source_neurons if n.orientation == orientation]
        for target_neuron in unit.receptive_neurons:
            for orientation in oriented_source_neurons:
                source_neurons = random_select_from_list(oriented_source_neurons[orientation], 2)
                for source_neuron in source_neurons:
                    synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
                    synapse.weight = 1
                    synapse.fixed = True


    def _connect_unit_to_single_orientation(self, unit: SelfSustainedActivityBlock, source_neurons: List[ReceptiveNeuron]):
        oriented_source_neurons = [n for n in source_neurons if n.orientation in unit.orientations]
        if not oriented_source_neurons:
            return
        for target_neuron in unit.receptive_neurons:
            source_neurons = random_select_from_list(oriented_source_neurons, unit.connection_density)
            for source_neuron in source_neurons:
                synapse = self.container.create_synapse(source=source_neuron, target=target_neuron)
                synapse.weight = 1
                synapse.fixed = True


    def on_sab_firing(self, sab):
        for region in self.regions:
            if region.sab_belongs_to(sab):
                region.on_sab_firing(sab)
