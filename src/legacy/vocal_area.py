import random

from lang.environment import Environment
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly
from common.file_ops import load_list_from_file
from common.misc import clean_punctuation
from lang.primitives.inter_area_message import InterAreaMessage


class VocalArea(NeuralArea):
    """
    Utters incoming speech signals
    """

    def __init__(self, name: str, agent: 'Agent'):
        from lang.assembly_builder import AssemblyBuilder
        super().__init__(name, agent)
        self.prefix = 'voc'
        self.modalities = [self.prefix]
        self.phonetics = {}
        self.environment = agent.environment
        self.speech_na: NeuralAssembly = None
        self.last_phonological_assembly_firing_tick = 0

    def on_fire(self, assembly: NeuralAssembly):
        if assembly != self.speech_na:
            self.environment.receive_utterance(assembly.cleaned_pattern)

    def allow_firing(self, na: NeuralAssembly):
        return self.agent.environment.current_tick in self.speech_na.firing_ticks

    def handle_message(self, msg: InterAreaMessage):
        if msg.name == 'assembly_attached_to_area' and msg.data['area'].name == 'phonological memory':
            source_na = msg.data['assembly']
            pattern = f'{self.prefix}: {source_na.cleaned_pattern}'
            na = self.builder.find_create_assembly(pattern)
            self.builder.check_create_connection(source=source_na, target=na)
            self._connect_to_speech_assembly(na)
            return True
        if msg.name == 'phonological_assembly_fired':
            self.last_phonological_assembly_firing_tick = self.agent.environment.current_tick
            # self.speech_na.firing_ticks.append(self.agent.environment.current_tick + 1)
        if msg.name == 'on_tick_beginning':
            if self.last_phonological_assembly_firing_tick < self.agent.environment.current_tick - 1\
                    and random.choice([True, False]):
                self.speech_na.firing_ticks.append(self.agent.environment.current_tick)
        return False

    def _connect_to_speech_assembly(self, assembly: NeuralAssembly):
        self.builder.check_create_connection(source=self.speech_na, target=assembly)

    def build_structure(self):
        self.speech_na = self.agent.assembly_builder.find_create_assembly('speech')
        self.speech_na.area = self
