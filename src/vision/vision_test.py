import os
import random

import matplotlib.pyplot as plt
import imageio

from neurons.network import Network
from neurons.neuro_container import NeuroContainer
from utils.misc import Colors
from vision.parameters import SabParameters
from vision.sab_layer import SabLayer
from vision.image import Image
from vision.receptive_layer import ReceptiveLayer, Orientation
from vision.sab_pooling_layer import SabPoolingLayer


def draw_vertical_line(img, x):
    img_height = img.shape[0]
    for y in range(img_height):
        img[y][x] = 0


def draw_horizontal_line(img, y):
    img_width = img.shape[1]
    for x in range(img_width):
        img[y][x] = 0


def train_on_image(receptive_layer, network, img, label, label_is_correct=True, max_ticks=60):
    network.clear_state()
    receptive_layer.attach_image(img)
    network.container.update_connectome_cache()
    network.gaba_release = not label_is_correct
    for sab in network.container.sabs:
        if sab.layer.layer_id == 3 and not sab.label:
            sab.label = label
            break
    network.run(max_ticks=max_ticks, label=label)


def infer_on_image(receptive_layer, network, img, max_ticks=20):
    network.clear_state()
    receptive_layer.attach_image(img)
    network.container.update_connectome_cache()
    network.gaba_release = False
    network.run(max_ticks=max_ticks)


def _print_layer_summary(layer):
    print('')
    for unit in layer.units:
        weight = _calc_average_weight(unit)
        print(f'{unit} weight: {weight:4.2f}')
    print('')


def _print_sab_summary(sab):
    if not sab:
        return
    print()
    print(Colors.bold(f'SAB {sab} stats:'))
    connections_with_upstream_sabs = {}
    for neuron in sab.receptive_neurons:
        for synapse in neuron.incoming_connections:
            if synapse.inhibitory:
                continue
            upstream_neuron = synapse.source
            upstream_sab = upstream_neuron.clump
            if upstream_sab != sab and upstream_sab.layer != sab.layer:
                if upstream_sab in connections_with_upstream_sabs:
                    connections_with_upstream_sabs[upstream_sab][0] += 1
                    connections_with_upstream_sabs[upstream_sab][1] += synapse.weight
                else:
                    connections_with_upstream_sabs[upstream_sab] = [1, synapse.weight]

    items = list(connections_with_upstream_sabs.items())
    items.sort(key=lambda x: x[0]._id)
    print('Strongly connected:')
    for item in items:
        stats = item[1]
        average_weight = stats[1] / stats[0]
        if average_weight >= 0.8:
            print(f'Upstream SAB {item[0]} connections: {stats[0]} average weight: {average_weight:4.2f}')
    print('')
    # print('Weekly connected:')
    # for item in items:
    #     stats = item[1]
    #     average_weight = stats[1] / stats[0]
    #     if average_weight < 0.8:
    #         print(f'Upstream SAB {item[0]} connections: {stats[0]} average weight: {average_weight:4.2f}')
    # print('')


def _print_hidden_sab_summary(sab, receptive_neurons):
    if not sab:
        return
    print(f'SAB {sab} stats:')
    connections_with_upstream_neurons = {}
    for neuron in sab.receptive_neurons:
        for synapse in neuron.incoming_connections:
            upstream_neuron = synapse.source
            if upstream_neuron in receptive_neurons:
                if upstream_neuron in connections_with_upstream_neurons:
                    connections_with_upstream_neurons[upstream_neuron][0] += 1
                    connections_with_upstream_neurons[upstream_neuron][1] += synapse.weight
                else:
                    connections_with_upstream_neurons[upstream_neuron] = [1, synapse.weight]

    items = list(connections_with_upstream_neurons.items())
    items.sort(key=lambda x: x[0]._id)
    print('Strongly connected:')
    for item in items:
        stats = item[1]
        average_weight = stats[1] / stats[0]
        if average_weight >= 0.8:
            print(f'Upstream neuron {item[0]} connections: {stats[0]} average weight: {average_weight:4.2f}')
    print('')
    print('Weekly connected:')
    for item in items:
        stats = item[1]
        average_weight = stats[1] / stats[0]
        if average_weight < 0.8:
            print(f'Upstream neuron {item[0]} connections: {stats[0]} average weight: {average_weight:4.2f}')
    print('')


def _calc_average_weight(sab):
    total_weight = 0
    num_synapses = 0
    for neuron in sab.receptive_neurons:
        for conn in neuron.incoming_connections:
            if conn.source.clump != sab and not conn.inhibitory:
                num_synapses += 1
                total_weight += conn.weight
    return total_weight / num_synapses


def show_receptive_map(receptive_layer, orientation):
    receptive_map = receptive_layer.get_firing_map(orientation=orientation)
    plt.imshow(receptive_map)
    plt.show(block=True)


def main():
    random.seed(24)
    container = NeuroContainer()

    receptive_layer = ReceptiveLayer(container=container)
    receptive_layer.allocate()

    num_ticks = 20
    output_sab_params = SabParameters()
    output_sab_params.interconnection_density = 0.8
    output_sab_params.receptive_synapse_weight = 0.6
    output_sab_params.inter_synapse_weight = 1
    output_sab_params.num_sad_neurons = 1
    output_sab_params.inhibitory_neurons_uppermost_threshold = 7
    output_sab_params.inhibitory_neurons_lowest_threshold = 4

    output_layer = SabLayer(layer_id=3, container=container, num_units=10, sab_params=output_sab_params)
    output_layer.is_output = True
    output_layer.allocate()

    hidden_sab_params = SabParameters()
    hidden_sab_params.interconnection_density = 0.3
    hidden_sab_params.receptive_synapse_weight = 1
    hidden_sab_params.inter_synapse_weight = 1
    hidden_sab_params.inhibitory_neurons_uppermost_threshold = 19
    hidden_sab_params.inhibitory_neurons_lowest_threshold = 19

    hidden_layer = SabPoolingLayer(
        layer_id=2,
        container=container,
        regions_shape=(3, 3),
        sab_params=hidden_sab_params
    )

    hidden_layer.allocate()

    output_layer.connect_to(hidden_layer, connection_density=2)

    hidden_layer.connect_to(receptive_layer)

    print(f'Allocated {len(container.neurons)} neurons and {len(container.synapses)} synapses')

    network = Network(container=container)

    sab001 = container.get_sab_by_id('001')

    path = '../data/images'
    imgP1 = Image(imageio.imread(os.path.join(path, 'П1.png')))
    imgP2 = Image(imageio.imread(os.path.join(path, 'П2.png')))
    imgR1 = Image(imageio.imread(os.path.join(path, 'р1.png')))
    imgR2 = Image(imageio.imread(os.path.join(path, 'р2.png')))
    imgR3 = Image(imageio.imread(os.path.join(path, 'р3.png')))


    # _print_sab_summary(sab001)
    # show_receptive_map(receptive_layer, Orientation.horizontal)
    receptive_neurons = list(receptive_layer.firing_history.keys())
    hidden_sabs = hidden_layer.get_all_sabs()
    sab002 = container.get_sab_by_id('002')
    # _print_hidden_sab_summary(sab24, receptive_neurons)
    # for sab in hidden_sabs:
    #     _print_hidden_sab_summary(sab, receptive_neurons)

    train_on_image(receptive_layer, network, imgP1, label='П', label_is_correct=True, max_ticks=num_ticks)
    train_on_image(receptive_layer, network, imgR1, label='р', label_is_correct=True, max_ticks=num_ticks)
    train_on_image(receptive_layer, network, imgR2, label='р', label_is_correct=True, max_ticks=num_ticks)
    # _print_sab_summary(sab002)
    train_on_image(receptive_layer, network, imgP1, label='р', label_is_correct=False, max_ticks=num_ticks)
    train_on_image(receptive_layer, network, imgR1, label='р', label_is_correct=True, max_ticks=num_ticks)
    train_on_image(receptive_layer, network, imgP2, label='П', label_is_correct=True, max_ticks=num_ticks)

    print('')
    print(Colors.bold('Inferencing..'))
    print('')

    infer_on_image(receptive_layer, network, imgP1)
    infer_on_image(receptive_layer, network, imgR3)

    winning_sab = output_layer.get_winning_sab()
    receptive_map = receptive_layer.get_firing_map(Orientation.horizontal)
    # plt.imshow(receptive_map)
    # plt.show(block=True)

    # network.run(max_ticks=60)

    # raw = misc.imread(os.path.join(path, 'П2.png'), flatten=0)
    # img2 = Image(raw)
    # train_on_image(receptive_layer, network, img2)

    # train_on_image(receptive_layer, network, img1)
    # x_right = img.detect_right_boundary(img)
    # draw_vertical_line(img, x_right)
    #
    # x_left = detect_left_boundary(img)
    # draw_vertical_line(img, x_left)
    #
    # y_upper = detect_upper_boundary(img)
    # draw_horizontal_line(img, y_upper)

    # plt.imshow(img1.source)
    # plt.colorbar()
    # plt.show()


if __name__ == '__main__':
    main()