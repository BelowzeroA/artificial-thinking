from typing import List, Set

# from lang.agent import Agent
from lang.neural_assembly import NeuralAssembly
from lang.primitives.inter_area_message import InterAreaMessage


class NeuralArea:
    """
    Neural area contains neural assemblies and undermines their properties and connectivity with other assemblies
    """
    def __init__(self, name: str, agent: 'Agent'):
        self.name = name
        self.agent = agent
        self.builder: 'AssemblyBuilder' = self.agent.assembly_builder
        self.modalities = []
        self.create_linked_assembly = True
        self.upstream_areas: List[NeuralArea] = []
        self.absorbs_dopamine = False
        self.winner_takes_it_all_strategy = False
        self.double_activation_from: List[NeuralArea] = []

    def corresponds_to_prefix(self, prefix: str) -> bool:
        return prefix in self.modalities

    def on_fire(self, na: NeuralAssembly):
        """
        Abstract method to react on the event of a neural assembly firing
        :param na:
        """
        pass

    def handle_message(self, msg: InterAreaMessage):
        return False

    def allow_firing(self, na: NeuralAssembly):
        """
        Adds additional conditions on whether to fire or not
        :param na:
        :return:
        """
        return True

    def build_structure(self):
        """
        Abstract method to build internal structure
        """
        pass

    def _repr(self):
        return f'[{self.name}]'

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()
