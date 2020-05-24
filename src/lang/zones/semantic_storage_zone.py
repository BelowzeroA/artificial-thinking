from typing import List

from lang.areas.semantic_storage_area import SemanticStorageArea
from lang.areas.speech_program_selector_area import SpeechProgramSelectorArea
from lang.assembly_source import AssemblySource
from lang.neural_zone import NeuralZone
from lang.zones.phonetic_recognition_zone import PhoneticRecognitionZone
from lang.zones.visual_recognition_zone import VisualRecognitionZone


class SemanticStorageZone(NeuralZone):
    """
    Takes input from phonetic and visual zones and builds a semantic world model
    Corresponds to the Anterior Temporal Lobe
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'SemStor'
        self.num_areas = 8
        self.areas: List[SemanticStorageArea] = []
        self._input_area: SemanticStorageArea = None
        self.prepare_areas()

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
                area.upstream_areas.append(prev_area)

    def connect_to(self, vr: VisualRecognitionZone, pr: PhoneticRecognitionZone):
        for vr_area in vr.output_areas():
            self._input_area.connect_to(vr_area)
        for pr_area in pr.output_areas():
            self._input_area.connect_to(pr_area)

    def prepare_assemblies(self, source: AssemblySource, tick: int):
        pass

    def before_assemblies_update(self, tick: int):
        for area in self.areas[1:]:
            area.before_assemblies_update(tick)