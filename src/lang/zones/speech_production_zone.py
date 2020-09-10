from typing import List

from lang.areas.semantic_storage_area import SemanticStorageArea
from lang.areas.speech_program_selector_area import SpeechProgramSelectorArea
from lang.assembly_source import AssemblySource
from lang.neural_zone import NeuralZone
from lang.zones.phonetic_recognition_zone import PhoneticRecognitionZone
from lang.zones.visual_recognition_zone import VisualRecognitionZone


class SpeechProductionZone(NeuralZone):
    """
    Responsible for speech production (voicing)
    Takes input from Speech Controller. Any input is considered as an utterance and immediately goes to console
    Corresponds to the Laryngeal Motor Cortex
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'SpProd'
        self._input_area: SemanticStorageArea = None
        self.prepare_areas()

    def prepare_areas(self):
        self._input_area = SemanticStorageArea('area', self.agent, self)

    def connect_to(self, zones: List[NeuralZone]):
        for zone in zones:
            for area in zone.output_areas():
                self._input_area.connect_to(area)

    def prepare_assemblies(self, source: AssemblySource, tick: int):
        pass

    def before_assemblies_update(self, tick: int):
        pass