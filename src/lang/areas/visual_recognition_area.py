from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea


class VisualRecognitionArea(NeuralArea):
    """
     Represents a single layer in the hierarchy of VisualRecognitionZone
     """
    def __init__(self, name: str, agent, zone):
        from lang.assembly_builder import AssemblyBuilder
        super().__init__(name, agent, zone)
        self.phonetics = {}
        self.threshold = HyperParameters.phonetic_recognition_threshold
        self.builder: AssemblyBuilder = None

