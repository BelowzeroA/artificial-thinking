from typing import List

from lang.areas.visual_lexicon.visual_lexicon_area import VisualLexiconArea
from lang.areas.visual_lexicon.visual_lexicon_selector_area import VisualLexiconSelectorArea
from lang.neural_zone import NeuralZone


class VisualLexiconZone(NeuralZone):
    """
    Takes input from Visual Recognition and Named Visual Objects zones and builds a lexicon of visual objects
    Corresponds to the Posterior Superior Temporal Sulcus (pSTS)
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'VL'
        self.num_areas = 1
        self._input_area: VisualLexiconArea = None
        self._output_area: VisualLexiconSelectorArea = None
        self.prepare_areas()

    @property
    def output_area(self):
        return self._output_area

    def prepare_areas(self):
        self._input_area = VisualLexiconArea.add(f'area_1', self.agent, self)
        self._output_area = VisualLexiconSelectorArea.add(f'output', self.agent, self)
        self._output_area.add_exciting_area(self._input_area)

    def output_areas(self):
        return [self._output_area]

    @property
    def output_tone_area(self):
        return self._output_area.tone_area

    def connect_to(self, zones: List[NeuralZone]):
        for zone in zones:
            for area in zone.output_areas():
                self._input_area.connect_to(area)

    # def before_assemblies_update(self, tick: int):
    #     self._input_area.before_assemblies_update(tick)
    #     self._output_area.before_assemblies_update(tick)