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
        self.num_areas = 2
        self.num_layers = 1
        self.areas: List[SemanticStorageArea] = []
        self._input_area: SemanticStorageArea = None
        self._output_area: SemanticStorageArea = None
        self.prepare_areas()

    def make_layer(self, ind: int):
        area = SemanticStorageArea.add(f'area_{ind + 1}', self.agent, self)
        if ind > 0:
            area.inhibits_itself = True
        areas = [area]
        for j in range(self.num_layers - ind + 1):
            projected_area = SemanticStorageArea.add(f'proj_area_{ind + 1}_{j + 1}', self.agent, self)
            prev_area = area if j == 0 else areas[j]
            projected_area.add_exciting_area(prev_area)
            areas.append(projected_area)
        self.areas.append(area)
        return areas

    def prepare_areas(self):
        self._output_area = SemanticStorageArea.add(f'output', self.agent, self)
        self._output_area.allows_assembly_merging = False
        self._output_area.winner_takes_it_all_strategy = True
        layer_areas = []
        for i in range(self.num_layers):
            areas = self.make_layer(i)
            layer_areas.append(areas)
            area_zero = areas[0]
            if i > 0:
                skip_factor = i - 1
                prev_layer_areas = layer_areas[i - 1]
                for prev_area in prev_layer_areas[2:]:
                    prev_area.add_inhibiting_area(area_zero)
                for prev_area in prev_layer_areas[:2 + skip_factor: skip_factor + 1]:
                    area_zero.add_exciting_area(prev_area)
                if i > 1:
                    prev_prev_layer_areas = layer_areas[i - 2]
                    # area_zero.add_exciting_area(prev_prev_layer_areas[0])
            else:
                self._input_area = area_zero
            last_layer_area = areas[-1:][0]
            self._output_area.add_exciting_area(last_layer_area)

    def output_areas(self):
        return [self._output_area]

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