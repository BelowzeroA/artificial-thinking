from typing import List

from lang.areas.speech_production_area import SpeechProductionArea
from lang.assembly_source import AssemblySource
from lang.neural_area import NeuralArea
from lang.neural_zone import NeuralZone


class SpeechProductionZone(NeuralZone):
    """
    Responsible for speech production
    Takes input from Speech Controller. Any input is considered as an utterance and immediately goes to console
    Corresponds to the Inferior Frontal Gyrus (IFG)
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'SpProd'
        self._input_area: SpeechProductionArea = None
        self.prepare_areas()

    @property
    def input_area(self) -> NeuralArea:
        return self._input_area

    def prepare_areas(self):
        self._input_area = SpeechProductionArea.add('area', self.agent, self)

    def connect_to(self, zones: List[NeuralZone]):
        for zone in zones:
            for area in zone.output_areas():
                self._input_area.connect_to(area)

    def prepare_assemblies(self, source: AssemblySource, tick: int):
        pass

    def before_assemblies_update(self, tick: int):
        pass