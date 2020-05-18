from lang.areas.speech_program_selector_area import SpeechProgramSelectorArea
from lang.neural_zone import NeuralZone


class SyntaxProductionZone(NeuralZone):
    """
    Converts a tree-like stream of concepts into a syntactically correct sentence
    Corresponds to the Broca's Area (Inferior Frontal Gyrus)
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.num_areas = 8
        self.program_selector_area: SpeechProgramSelectorArea = None
        self.action_area: SpeechProgramSelectorArea = None
        self._input_area = None
        self.prepare_areas()

    def prepare_areas(self):
        pass

    def prepare_assemblies(self, source, tick: int):
        current_planned_tick = tick
        for word in source.words:
            current_planned_tick = self._prepare_assemblies_for_word(word, current_planned_tick)
            current_planned_tick += 1

    def _prepare_assemblies_for_word(self, word: str, tick: int) -> int:
        return self.builder.build_phonemes_from_word(word, area=self._input_area, starting_tick=tick)

    def before_assemblies_update(self, tick: int):
        pass