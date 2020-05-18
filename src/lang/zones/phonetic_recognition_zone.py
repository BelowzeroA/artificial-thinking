from typing import List

from lang.areas.phonetic_recognition_area import PhoneticRecognitionArea
from lang.assembly_source import AssemblySource
from lang.neural_zone import NeuralZone


class PhoneticRecognitionZone(NeuralZone):
    """
    Recognizes phonemes, syllables, and spoken words
    Corresponds to the Anterior Superior Temporal Gyrus (aSTG)
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.num_areas = 8
        self.areas: List[PhoneticRecognitionArea] = []
        self._input_area = None
        self._output_area = None
        self.prepare_areas()

    def prepare_areas(self):
        self._output_area = PhoneticRecognitionArea(f'output', self.agent)
        for i in range(self.num_areas):
            area = PhoneticRecognitionArea(f'area_{i}', self.agent)
            self.agent.container.add_area(area)
            if i == 0:
                self._input_area = area
                area.winner_takes_it_all_strategy = False
            else:
                self._output_area.upstream_areas.append(area)
            self.areas.append(area)
            if i > 0:
                prev_area = self.areas[i - 1]
                area.upstream_areas.append(prev_area)

    def output_areas(self):
        return self.areas[1:]

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