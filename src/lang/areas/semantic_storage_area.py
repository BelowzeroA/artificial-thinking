from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea


class SemanticStorageArea(NeuralArea):
    """
     Represents a single layer in the hierarchy of PhoneticRecognitionZone
     """
    def __init__(self, name: str, agent, zone):
        from lang.assembly_builder import AssemblyBuilder
        super().__init__(name, agent, zone)
        self.phonetics = {}
        self.threshold = HyperParameters.phonetic_recognition_threshold
        self.builder: AssemblyBuilder = None
        self.allows_assembly_merging = True
        self.allows_projection = False

    def before_assemblies_update(self, tick: int):
        assemblies = [na for na in self.agent.container.assemblies if na.area == self]
        if assemblies:
            assemblies_potentials = [(na, na.potential) for na in assemblies]
            assemblies_potentials.sort(key=lambda x: x[1], reverse=True)
            max_assembly_potential = assemblies_potentials[0]
            if max_assembly_potential[1] >= HyperParameters.phonetic_recognition_threshold:
                na = max_assembly_potential[0]
                na.is_winner = True

