from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea


class SpeechProductionArea(NeuralArea):
    """
     Represents an agent's utterance
     """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.threshold = 1
        self.allows_projection = True

    def _find_phonetic_pattern(self, assembly: 'NeuralAssembly') -> str:
        if len(assembly.source_assemblies) == 2:
            phonetic_assemblies = [na for na in assembly.source_assemblies if na.area.zone.short_name != 'VR']
            if len(phonetic_assemblies) == 2:
                return assembly.pattern
            elif len(phonetic_assemblies) == 1:
                return self._find_phonetic_pattern(phonetic_assemblies[0])
            else:
                return None
        elif len(assembly.source_assemblies) == 1:
            return self._find_phonetic_pattern(assembly.source_assemblies[0])
        else:
            return assembly.pattern

    def on_fire(self, na: 'NeuralAssembly'):
        super().on_fire(na)
        phonetic_pattern = self._find_phonetic_pattern(na)
        # self.agent.environment.receive_utterance(phonetic_pattern)
        self.agent.utter(phonetic_pattern)
        # print(f'Agent said: {phonetic_pattern}')

