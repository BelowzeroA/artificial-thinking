from typing import List


class NeuralArea:
    """
    Neural area contains neural assemblies and undermines their properties and connectivity with other assemblies
    """
    def __init__(self, name: str):
        self.name = name
        self.modalities = []
        self.create_linked_assembly = True
        self.upstream_areas: List[NeuralArea] = []
        self.absorbs_dopamine = False
        self.double_activation_from: List[NeuralArea] = []
        # self.prefixes = []

    def corresponds_to_prefix(self, prefix: str) -> bool:
        return prefix in self.modalities

    # def add_projected_area(self, a: 'NeuralArea'):
    #     self.projected_to.append(a)

    def _repr(self):
        return f'[{self.name}]'

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()
