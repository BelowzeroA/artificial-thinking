from typing import List

from lang.areas.semantic_storage_area import SemanticStorageArea
from lang.areas.speech_program_selector_area import SpeechProgramSelectorArea
from lang.assembly_source import AssemblySource
from lang.neural_zone import NeuralZone
from lang.zones.phonetic_recognition_zone import PhoneticRecognitionZone
from lang.zones.visual_recognition_zone import VisualRecognitionZone


class VisualLexiconZone(NeuralZone):
    """
    Takes input from visual recognition and semantic storage zones and builds a lexicon of visual objects
    Corresponds to the Posterior Middle Temporal Gyrus
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'VL'
        self.num_areas = 1
        self.areas: List[SemanticStorageArea] = []
        self._input_area: SemanticStorageArea = None
        self._output_area: SemanticStorageArea = None
        self.prepare_areas()

    @property
    def output_area(self):
        return self._output_area

    def prepare_areas(self):
        for i in range(self.num_areas):
            area = SemanticStorageArea(f'area_{i}', self.agent, self)
            self.agent.container.add_area(area)
            if i == 0:
                self._input_area = area
                area.winner_takes_it_all_strategy = False
            self.areas.append(area)
            if i > 0:
                prev_area = self.areas[i - 1]
                area.add_exciting_area(prev_area)
            self._output_area = area

    def output_areas(self):
        return [self._output_area]

    def connect_to(self, zones: List[NeuralZone]):
        for zone in zones:
            for area in zone.output_areas():
                self._input_area.connect_to(area)

    def prepare_assemblies(self, source: AssemblySource, tick: int):
        pass

    def before_assemblies_update(self, tick: int):
        for area in self.areas[1:]:
            area.before_assemblies_update(tick)