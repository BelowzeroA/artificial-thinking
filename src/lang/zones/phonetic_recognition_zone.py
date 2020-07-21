from typing import List

from lang.areas.phonetic_recognition_area import PhoneticRecognitionArea
from lang.areas.phonetic_recognition_projected_area import PhoneticRecognitionProjectedArea
from lang.assembly_source import AssemblySource
from lang.neural_zone import NeuralZone


class PhoneticRecognitionZone(NeuralZone):
    """
    Recognizes phonemes, syllables, and spoken words
    Corresponds to the Anterior Superior Temporal Gyrus (aSTG)
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'PR'
        self.num_layers = 3
        self.areas: List[PhoneticRecognitionArea] = []
        self.projected_areas: List[PhoneticRecognitionProjectedArea] = []
        self._input_area = None
        self._output_area = None
        self.prepare_areas()

    def make_layer(self, ind: int):
        area = PhoneticRecognitionArea.add(f'area_{ind + 1}', self.agent, self)
        if ind > 0:
            area.inhibits_itself = True
        areas = [area]
        for j in range(self.num_layers - ind + 2):
            projected_area = PhoneticRecognitionProjectedArea.add(f'proj_area_{ind + 1}_{j + 1}', self.agent, self)
            prev_area = area if j == 0 else areas[j]
            projected_area.add_exciting_area(prev_area)
            areas.append(projected_area)
        self.areas.append(area)
        return areas

    def prepare_areas(self):
        self._output_area = PhoneticRecognitionProjectedArea.add(f'output', self.agent, self)
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
                
    # def prepare_areas0(self):
    #     self._output_area = PhoneticRecognitionProjectedArea.add(f'output', self.agent, self)
    #     self._output_area.allows_assembly_merging = False
    #     self._output_area.winner_takes_it_all_strategy = True
    #     for i in range(self.num_layers):
    #         area = PhoneticRecognitionArea.add(f'area_{i}', self.agent, self)
    #         for j in range(4 - i):
    #             projected_area = PhoneticRecognitionProjectedArea.add(f'proj_area_{i}_{j}', self.agent, self)
    #             projected_area.add_upstream_area(area)
    #         self.areas.append(area)
    #         self.projected_areas.append(projected_area)
    #         if i == 0:
    #             self._input_area = area
    #             area.winner_takes_it_all_strategy = False
    #         else:
    #             self._output_area.add_upstream_area(area)
    #         if i > 0:
    #             prev_area = self.areas[i - 1]
    #             prev_projected_area = self.projected_areas[i - 1]
    #             area.add_upstream_area(prev_area)
    #             area.add_upstream_area(prev_projected_area)

    def output_areas(self):
        return [self._output_area]

    def prepare_assemblies(self, source: AssemblySource, tick: int):
        current_planned_tick = tick
        for word in source.words:
            current_planned_tick = self._prepare_assemblies_for_word(word, current_planned_tick)
            current_planned_tick += 1

    def _prepare_assemblies_for_word(self, word: str, tick: int) -> int:
        return self.builder.build_phonemes_from_word(word, area=self._input_area, starting_tick=tick)

    def before_assemblies_update(self, tick: int):
        for area in self.areas[1:]:
            area.before_assemblies_update(tick)
        self._output_area.before_assemblies_update(tick)