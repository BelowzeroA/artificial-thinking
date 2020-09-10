from typing import List

from lang.areas.speech_program_selector_area import SpeechProgramSelectorArea
from lang.neural_area import NeuralArea
from lang.neural_zone import NeuralZone


class SyntaxProductionZone(NeuralZone):
    """
    Converts a tree-like stream of concepts into a syntactically correct sentence
    Corresponds to the Broca's Area (Inferior Frontal Gyrus)
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'BRa'
        self.num_areas = 1
        self.program_selector_area: SpeechProgramSelectorArea = None
        self.action_area: SpeechProgramSelectorArea = None
        self._input_area = None
        self._output_area = None
        self.prepare_areas()

    @property
    def input_area(self) -> NeuralArea:
        return self._input_area

    def prepare_areas(self):
        self._input_area = SpeechProgramSelectorArea.add('input', agent=self.agent, zone=self)
        self._input_area.allows_projection = True
        self._output_area = self._input_area

    def connect_to(self, zones: List[NeuralZone]):
        for zone in zones:
            for area in zone.output_areas():
                self._input_area.connect_to(area)

    def prepare_assemblies(self, source, tick: int):
        current_planned_tick = tick

    def before_assemblies_update(self, tick: int):
        # for area in self.areas[1:]:
        #     area.before_assemblies_update(tick)
        self._output_area.before_assemblies_update(tick)

    def output_areas(self):
        return [self._output_area]
