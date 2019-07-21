import random

import os

from lang.assembly_builder import AssemblyBuilder
from lang.data_provider import DataProvider
from lang.network import Network
from lang.neural_area import NeuralArea
from lang.phonetics_dict import PhoneticsDict
from neurons.neuro_container import NeuroContainer


def init_areas():
    sensory_na = NeuralArea('sensory')
    sensory_na.modalities = ['v', 'o']
    actions_na = NeuralArea('actions')
    actions_na.modalities = ['a']
    return [sensory_na, actions_na]


def main():
    data_dir = '../data/lang/'
    random.seed(24)
    container = NeuroContainer()
    container.add_areas(init_areas())
    phonetics_dict = PhoneticsDict(os.path.join(data_dir, 'phonetics_eng.txt'))
    dp = DataProvider(os.path.join(data_dir, 'stage3.txt'))

    assembly_builder = AssemblyBuilder(container=container, data_provider=dp, phonetics=phonetics_dict)
    assembly_builder.build_phonemes_from_text(os.path.join(data_dir, 'phonetics_learning.txt'))

    network = Network(container=container, assembly_builder=assembly_builder)
    network.run(max_ticks=100)


if __name__ == '__main__':
    main()