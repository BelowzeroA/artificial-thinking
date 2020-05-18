import itertools

from typing import List

from neurons.neuro_container import NeuroContainer
from vision.common import Coord
from vision.parameters import SabParameters
from vision.receptive_layer import Orientation
from vision.sab_layer import SabLayer


class SabComboLayer(SabLayer):
    """
    Region of self-sustained activity blocks where each block is connected with each other by inhibitory synapses
    realising "The winner takes it all" strategy
    """
    def __init__(self, container: NeuroContainer, num_units: int, coord: Coord,
                 layer_id, parent_layer, sab_params: SabParameters):
        super().__init__(container=container, num_units=num_units,
                         layer_id=layer_id, parent_layer=parent_layer, sab_params=sab_params)
        self.coord = coord
        self.supported_orientations = [Orientation.horizontal, Orientation.vertical]


    def allocate(self):
        self.allocate_orientation_sabs()
        self.allocate_orientation_combinations_sabs()
        # self._allocate_inhibitory_synapses()


    def allocate_orientation_sabs(self):
        for orientation in self.supported_orientations:
            self.allocate_orientation_sab(orientations=[orientation], connection_density=4)
            self.allocate_orientation_sab(orientations=[orientation], connection_density=8)
            self.allocate_orientation_sab(orientations=[orientation], connection_density=12)


    def allocate_orientation_combinations_sabs(self):
        combinations = list(itertools.combinations_with_replacement(self.supported_orientations, 2))
        for combination in combinations:
            if combination[0] != combination[1]:
                self.allocate_orientation_sab(orientations=[combination[0], combination[1]])


    def allocate_orientation_sab(self, orientations: List[Orientation], connection_density: int = 0):
        sab = self.container.create_sab(layer=self.parent_layer, params=self.sab_params)
        sab.region = self
        sab.orientations = orientations
        sab.connection_density = connection_density
        sab.allocate()
        self.units.append(sab)
