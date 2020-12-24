from lang.areas.phrase_integrator.phrase_integrator_area import PhraseIntegratorArea
from lang.areas.phrase_integrator.phrase_integrator_sync_area import PhraseIntegratorSyncArea
from lang.neural_zone import NeuralZone
from lang.zones.named_visual_objects_zone import NamedVisualObjectsZone
from lang.zones.phonetic_recognition_zone import PhoneticRecognitionZone


class PhraseIntegratorZone(NeuralZone):
    """
    Integrates the streams from Phonetic recognizer and Named visual objects zones
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'PhrInt'
        self._phonetic_input = None
        self._output_area = None
        self.prepare_areas()

    def prepare_areas(self):
        self._phonetic_input = PhraseIntegratorSyncArea.add('sync', self.agent, self)
        self._output_area = PhraseIntegratorArea.add(f'output', self.agent, self)
        self._output_area.add_exciting_area(self._phonetic_input)

    def output_areas(self):
        return [self._output_area]

    def connect_to(self, pr: PhoneticRecognitionZone, nvo: NamedVisualObjectsZone):
        for pr_area in pr.output_areas():
            self._phonetic_input.connect_to(pr_area)

        for nvo_area in nvo.output_tone_areas():
            self._output_area.connect_to(nvo_area)