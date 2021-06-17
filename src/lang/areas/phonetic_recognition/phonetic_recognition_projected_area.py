from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea


class PhoneticRecognitionProjectedArea(NeuralArea):
    """
     Represents a projection from a basic neural area of PhoneticRecognitionZone
     """
    def __init__(self, name: str, agent, zone):
        from lang.assembly_builder import AssemblyBuilder
        super().__init__(name, agent, zone)
        self.phonetics = {}
        self.threshold = HyperParameters.phonetic_recognition_threshold
        self.builder: AssemblyBuilder = None
        self.winner_takes_it_all_strategy = False
        self.allows_assembly_merging = False
        self.allows_projection = True

    def before_assemblies_update(self, tick: int):
        self.check_set_is_winner(threshold=HyperParameters.phonetic_recognition_threshold)


