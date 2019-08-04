import random

import os
from typing import List

from lang.assembly_builder import AssemblyBuilder
from lang.data_provider import DataProvider
from lang.network import Network
from lang.neural_area import NeuralArea
from lang.phonetics_dict import PhoneticsDict
from neurons.neuro_container import NeuroContainer


def _add_area(container: NeuroContainer,
              name: str,
              modalities: List[str]=None,
              upstream_areas: List[NeuralArea]=None,
              create_linked_assembly=True):
    area = NeuralArea(name)
    container.add_area(area)
    if modalities:
        area.modalities = modalities
    if upstream_areas:
        area.upstream_areas = upstream_areas
    area.create_linked_assembly = create_linked_assembly
    return area


def init_areas(container: NeuroContainer):
    sensory_na = _add_area(container, 'sensory', ['v', 'o'])

    sensory_joint = _add_area(container, 'sensory joint', None, [sensory_na], False)

    actions_na = _add_area(container, 'actions', ['a'])

    phonetic_na = _add_area(container, 'phonetic', ['ph'])

    actions_observations = _add_area(container, 'actions with observations', None, [sensory_joint, actions_na], False)
    actions_observations.double_activation_from.append(sensory_joint)
    actions_observations.absorbs_dopamine = True

    actions_na.double_activation_from.append(actions_observations)

    default_na = NeuralArea('default')
    container.default_area = default_na


def main():
    data_dir = '../data/lang/'
    random.seed(24)

    container = NeuroContainer()
    init_areas(container)

    phonetics_dict = PhoneticsDict(os.path.join(data_dir, 'phonetics_eng.txt'))
    dp = DataProvider(os.path.join(data_dir, 'stage3.txt'))

    assembly_builder = AssemblyBuilder(container=container, data_provider=dp, phonetics=phonetics_dict)
    assembly_builder.build_phonemes_from_text(os.path.join(data_dir, 'phonetics_learning.txt'))

    network = Network(container=container, assembly_builder=assembly_builder)
    network.run(max_ticks=100)


if __name__ == '__main__':
    main()