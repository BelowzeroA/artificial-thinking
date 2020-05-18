from lang.areas.speech_program_selector_area import SpeechProgramSelectorArea
from lang.neural_zone import NeuralZone


class SpeechControllerZone(NeuralZone):
    """
    Controls other zones gating (inhibition/activation) to allow speech production
    Corresponds to the Ventro-Lateral Pre-Frontal Cortex (VLPFC)
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.program_selector_area: SpeechProgramSelectorArea = None
        self.action_area: SpeechProgramSelectorArea = None
        self._input_area = None
        self.prepare_areas()

    def prepare_areas(self):
        pass

    def prepare_assemblies(self, source, tick: int):
        pass

    def before_assemblies_update(self, tick: int):
        return
        for area in self.areas[1:]:
            area.before_assemblies_update(tick)