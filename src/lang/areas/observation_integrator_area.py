import random

from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.primitives.inter_area_message import InterAreaMessage


class ObservationIntegratorArea(NeuralArea):
    """
    Integrates outgoing assemblies from different zones to a single compound assembly
    """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.allows_assembly_merging = True
        self.allows_projection = True

    def before_assemblies_update(self, tick: int):
        pass

