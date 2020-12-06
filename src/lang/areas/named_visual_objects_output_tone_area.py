from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea


class NamedVisualObjectsOutputToneArea(NeuralArea):
    """
     An output area of NamedVisualObjectsZone for tone signalling
     """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.sends_tone = True
        self.assembly = self.agent.assembly_builder.find_create_assembly(f'{self.zone}: {self.name}', area=self)



