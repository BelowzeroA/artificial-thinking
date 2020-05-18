from collections import namedtuple

Coord = namedtuple('Coord', ['x', 'y'])
FiringHistory = namedtuple('FiringHistory', ['tick', 'potential', 'external_excitation'])