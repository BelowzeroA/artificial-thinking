# from lang.areas.semantic_storage_area import SemanticStorageArea
from lang.areas.named_visual_objects.named_visual_objects_area import NamedVisualObjectsArea
from lang.areas.named_visual_objects.named_visual_objects_selector_area import NamedVisualObjectsSelectorArea
from lang.neural_zone import NeuralZone
from lang.zones.phonetic_recognition_zone import PhoneticRecognitionZone
from lang.zones.visual_recognition_zone import VisualRecognitionZone


class NamedVisualObjectsZone(NeuralZone):
    """
    Takes input from phonetic and visual zones and builds a hierarchy of named visual objects
    Corresponds to the Anterior Temporal Lobe (ATL)
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'NamedVO'
        self._input_area: NamedVisualObjectsArea = None
        self._output_area: NamedVisualObjectsArea = None
        self.prepare_areas()

    def prepare_areas(self):
        self._input_area = NamedVisualObjectsArea.add(f'area_1', self.agent, self)
        self._output_area = NamedVisualObjectsSelectorArea.add(f'output', self.agent, self)
        self._output_area.add_exciting_area(self._input_area)

    def output_areas(self):
        return [self._output_area]

    def output_tone_areas(self):
        return [self._output_area.tone_area]

    def connect_to(self, vr: VisualRecognitionZone, pr: PhoneticRecognitionZone):
        for vr_area in vr.output_areas():
            self._input_area.connect_to(vr_area)
        for pr_area in pr.output_areas():
            self._input_area.connect_to(pr_area)
