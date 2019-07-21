import random
from math import floor, ceil

import numpy as np

from brain.brain import Brain
from neurons.layer import Layer
from neurons.neuro_container import NeuroContainer
from vision.common import Coord
from vision.image import Image
from vision.parameters import HyperParameters

MIN_NUM_DENDRITES = 6
STRIDE = 2


class Orientation:
    vertical = 1
    horizontal = 2
    right_45 = 3
    left_45 = 4
    right_22 = 5
    right_67 = 6
    left_22 = 7
    left_67 = 8


class ReceptiveLayer(Layer):

    def __init__(self, container: NeuroContainer):
        super().__init__(container)
        self.width = HyperParameters.neural_grid_width
        self.height = HyperParameters.neural_grid_height
        self.img: Image = None
        self.vertical_stride = 0
        self.horizontal_stride = 0
        self.pixels_map = {}
        self.firing_history = {}


    def attach_image(self, img: Image):
        self.img = img
        for neuron in self.neurons:
            neuron.receptive_field.clear()
        self._create_pixels_2_neurons_map()
        for y in range(img.height):
            self._allocate_horizontal_line(img, y)
        for x in range(img.width):
            self._allocate_vertical_line(img, x)
        for x in range(img.width):
            self._allocate_right_45(img, x)


    def _create_pixels_2_neurons_map(self):
        width_pixel_map = {}
        height_pixel_map = {}

        if self.img.width > self.width:
            self._fill_pixel_map(width_pixel_map, self.img.width, self.width)
        else:
            self._pad_pixel_map(width_pixel_map, self.img.width, self.width)

        if self.img.height > self.height:
            self._fill_pixel_map(height_pixel_map, self.img.height, self.height)
        else:
            self._pad_pixel_map(height_pixel_map, self.img.height, self.height)

        self.pixels_map.clear()
        for x in width_pixel_map:
            neuron_x = width_pixel_map[x]
            if neuron_x is not None:
                for y in height_pixel_map:
                    neuron_y = height_pixel_map[y]
                    if neuron_y is not None:
                        coord = Coord(x=x, y=y)
                        self.pixels_map[coord] = Coord(x=neuron_x, y=neuron_y)


    def _pad_pixel_map(self, pixel_map, img_dim, grid_dim):
        diff = grid_dim - img_dim
        diff_half = int(diff / 2)
        for pixel in range(img_dim):
            pixel_map[pixel] = pixel + diff_half


    def _fill_pixel_map(self, pixel_map, img_dim, grid_dim):
        diff = img_dim - grid_dim
        diff_half = int(diff / 2)
        diff_for_edge = round(diff_half / 3 * 2)
        diff_for_middle = diff_half - diff_for_edge
        third_of_half = int(img_dim / 2 / 3)
        skips_for_middle = img_dim - grid_dim - diff_for_edge * 2 - diff_for_middle * 2
        neuron_counter = 0
        neuron_counter = self._map_pixels_on_interval(pixel_map, img_dim, 0, third_of_half - 1,
                                                      diff_for_edge, neuron_counter)
        neuron_counter = self._map_pixels_on_interval(pixel_map, img_dim, third_of_half, third_of_half * 2 - 1,
                                                      diff_for_middle, neuron_counter)
        neuron_counter = self._map_pixels_on_interval(pixel_map, img_dim, third_of_half * 2,
                                                      img_dim - third_of_half * 2 - 1, skips_for_middle, neuron_counter)
        neuron_counter = self._map_pixels_on_interval(pixel_map, img_dim, img_dim - third_of_half * 2,
                                                      img_dim - third_of_half - 1, diff_for_middle, neuron_counter)
        neuron_counter = self._map_pixels_on_interval(pixel_map, img_dim, img_dim - third_of_half, img_dim - 1,
                                                      diff_for_edge, neuron_counter)


    def _map_pixels_on_interval(self, pixel_map, img_dim, interval_start, interval_end, num_skips, neuron_counter):
        num_neurons = interval_end - interval_start - num_skips + 1
        if num_neurons > num_skips:
            allocation = self._allocate_neurons_among_skips(interval_start, interval_end, num_skips, num_neurons)
            allocation = [1 - v for v in allocation]
        else:
            allocation = self._allocate_neurons_among_skips(interval_start, interval_end, num_neurons, num_skips)
        index = 0
        for pixel_index in range(img_dim):
            if pixel_index in range(interval_start, interval_end + 1):
                if allocation[index] == 0:
                    value = None
                else:
                    value = neuron_counter
                    neuron_counter += 1
                pixel_map[pixel_index] = value
                index += 1
        return neuron_counter


    @staticmethod
    def _allocate_neurons_among_skips(interval_start, interval_end, num_allocated, num_rest):
        alloc_step = int(num_rest / num_allocated) + 1 if num_allocated > 0 else 1
        indices = []
        for x in range(interval_start, interval_end):
            left_to_allocate = num_allocated - len(indices)
            if left_to_allocate == 0:
                break
            points_left = interval_end - x
            if points_left <= left_to_allocate:
                indices.append(x)
            elif x % alloc_step == 0:
                indices.append(x)

        allocation = []
        for x in range(interval_start, interval_end + 1):
            if x in indices:
                allocation.append(1)
            else:
                allocation.append(0)
        return allocation


    def allocate(self):
        ors = [Orientation.__dict__[key] for key in Orientation.__dict__ if not key.startswith('_')]
        for x_coord in range(self.width):
            for y_coord in range(self.height):
                for orientation in ors:
                    self._allocate_neuron(x_coord, y_coord, orientation)


    def _allocate_neuron(self, x, y, orientation):
        from vision.receptive_neuron import ReceptiveNeuron

        coord = Coord(x=x, y=y)
        neuron = ReceptiveNeuron(
            self.container.next_neuron_id(),
            container=self.container,
            coord=coord,
            layer=self,
            orientation=orientation)
        self.container.append_neuron(neuron)
        self.neurons.append(neuron)
        return neuron


    def get_firing_map(self, orientation):
        arr = np.zeros(shape=(self.height, self.width))
        for neuron in self.neurons:
            if neuron.fired and neuron.orientation == orientation:
                arr[neuron.coord.y, neuron.coord.x] = 1
        return arr


    def on_neuron_firing(self, neuron):
        if neuron in self.firing_history:
            self.firing_history[neuron] += 1
        else:
            self.firing_history[neuron] = 1


    def _get_neuron_clear(self, x, y, orientation):
        coord = Coord(x=x, y=y)
        if coord not in self.pixels_map:
            return None
        neuron_coord = self.pixels_map[coord]
        neurons = [n for n in self.neurons if n.coord == neuron_coord and n.orientation == orientation]
        neuron = neurons[0]
        neuron.receptive_field.clear()
        return neuron


    def _get_neuron_clear0(self, x, y, orientation):
        neurons = [n for n in self.neurons if n.coord.x == x and n.coord.y == y and n.orientation == orientation]
        neuron = neurons[0]
        neuron.receptive_field.clear()
        return neuron


    def _allocate_horizontal_line(self, img: Image, y_coord):
        stride = img.width / self.width
        stride = 1 if stride < 1 else int(stride)
        num_dendrites = max(MIN_NUM_DENDRITES, stride * 2)

        for i in range(self.width - 1):
            neuron = self._get_neuron_clear(i, y_coord, Orientation.horizontal)
            if not neuron:
                continue
            for x_shift in range(num_dendrites):
                x_coord = i * stride + x_shift
                if x_coord >= img.width:
                    break
                neuron.receptive_field.append(Coord(x=x_coord, y=y_coord))


    def _allocate_vertical_line(self, img: Image, x_coord):
        stride = img.height / self.height
        stride = 1 if stride < 1 else int(stride)
        num_dendrites = max(MIN_NUM_DENDRITES, stride * 2)

        for i in range(self.height - 1):
            neuron = self._get_neuron_clear(x_coord, i, Orientation.vertical)
            if not neuron:
                continue
            for y_shift in range(num_dendrites):
                y_coord = i * stride + y_shift
                if y_coord >= img.height:
                    break
                neuron.receptive_field.append(Coord(x=x_coord, y=y_coord))


    def _allocate_right_45(self, img: Image, x_coord):
        stride = img.height / self.height
        stride = 1 if stride < 1 else int(stride)
        num_dendrites = max(MIN_NUM_DENDRITES, stride * 2)
        if x_coord > img.width - num_dendrites:
            return
        middle_x = x_coord + round(num_dendrites / 2)
        for i in range(num_dendrites, self.height):
            middle_y = i - round(num_dendrites / 2) - 1
            neuron = self._get_neuron_clear(middle_x, middle_y, Orientation.right_45)
            if not neuron:
                continue
            for shift in range(num_dendrites):
                receptive_y = i * stride - shift - 1
                receptive_x = x_coord + shift
                if receptive_y < 0 or receptive_x >= img.width or receptive_y >= img.height:
                    break
                neuron.receptive_field.append(Coord(x=receptive_x, y=receptive_y))


    def fire_random_pattern(self, pattern_key: int):
        random.seed(pattern_key)
        neurons_copy = list(self.neurons)
        num_neurons = Brain.input_pattern_length
        neurons_to_fire = [neurons_copy.pop(random.randrange(len(neurons_copy))) for _ in range(num_neurons)]
        for neuron in neurons_to_fire:
            neuron.fire()
