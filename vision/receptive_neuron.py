from neurons.neuron import Neuron
from vision.common import Coord, FiringHistory
from vision.image import Image
from vision.parameters import HyperParameters
from vision.receptive_layer import ReceptiveLayer, Orientation


class ReceptiveNeuron(Neuron):
    """
    Neuron that receives input directly from Image
    """
    def __init__(self, id, container, coord: Coord, layer: ReceptiveLayer, orientation):
        super().__init__(id, container)
        self.receptive_field = []
        self.orientation = orientation
        self.coord = coord
        self.layer = layer


    def update(self):
        if self._is_active():
            self.firing = True

        if self.firing:
            self.layer.on_neuron_firing(self)
            self.fired = True
            self.firing = False
            super()._record_history_frame()
            for synapse in self.outgoing_connections:
                synapse.pulsing = True


    def _get_pixel_val(self, coord=None, x=0, y=0):
        img: Image = self.layer.img
        if coord:
            return img.source[coord.y][coord.x]
        else:
            return img.source[y][x]


    def _is_active(self):
        accumulated_difference = 0
        middle_x = int(self.layer.width / 2)
        middle_y = int(self.layer.height / 2)
        shift_x = 1 if self.coord.x <= middle_x else -1
        shift_y = 1 if self.coord.y <= middle_y else -1
        for coord in self.receptive_field:
            pixel_val = self._get_pixel_val(coord=coord)
            difference = 0
            if self.orientation == Orientation.vertical:
                difference = abs(pixel_val - self._get_pixel_val(x=coord.x + shift_x, y=coord.y))
            elif self.orientation == Orientation.horizontal:
                difference = abs(pixel_val - self._get_pixel_val(x=coord.x, y=coord.y + shift_y))
            if difference > HyperParameters.receptive_dendrite_threshold:
                accumulated_difference += 1

        return accumulated_difference > HyperParameters.receptive_neuron_threshold
