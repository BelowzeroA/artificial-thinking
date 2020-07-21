from typing import List

from lang.areas.phonetic_recognition_area import PhoneticRecognitionArea
from lang.areas.visual_recognition_area import VisualRecognitionArea
from lang.assembly_source import AssemblySource
from lang.hyperparameters import HyperParameters
from lang.neural_zone import NeuralZone


class VisualRecognitionZone(NeuralZone):
    """
    Recognizes visual objects
    Corresponds to the Inferior Temporal lobe (ITL)
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'VR'
        self.num_areas = 1
        self.areas: List[VisualRecognitionArea] = []
        self._input_area: VisualRecognitionArea = None
        self.prepare_areas()

    def output_areas(self):
        return [self._input_area]

    def prepare_areas(self):
        for i in range(self.num_areas):
            area = VisualRecognitionArea(f'area_{i}', self.agent, self)
            self.agent.container.add_area(area)
            if i == 0:
                self._input_area = area
            self.areas.append(area)

    def prepare_assemblies(self, source: AssemblySource, tick: int):
        firing_span = [t + tick for t in range(HyperParameters.visual_firing_span)]
        for vis in source.visuals:
            na = self.builder.find_create_assembly(pattern=vis, area=self._input_area)
            na.firing_ticks.extend(firing_span)

    def before_assemblies_update(self, tick: int):
        for area in self.areas[1:]:
            area.before_assemblies_update(tick)