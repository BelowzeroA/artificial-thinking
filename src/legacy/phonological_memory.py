from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly
from common.file_ops import load_list_from_file
from common.misc import clean_punctuation
from lang.primitives.inter_area_message import InterAreaMessage


class PhonologicalMemory(NeuralArea):
    """
    Converts speech signals into syllable assemblies
    """
    def __init__(self, name: str, agent):
        from lang.assembly_builder import AssemblyBuilder
        super().__init__(name, agent)
        self.phonetics = {}
        self.builder: AssemblyBuilder = None
        self.vocal_area: NeuralArea = None
        self.create_linked_assembly = True

    def handle_message(self, msg: InterAreaMessage):
        # if msg.name == 'assembly_attached_to_area' and msg.data['area'] == self:
        #     na = msg.data['assembly']
        #     if not na.is_link:
        #         na.firing_count = HyperParameters.phonological_na_firing_count
        #     return True
        return False

    def prepare_phoneme_assemblies0(self, starting_tick: int, token: str) -> int:
        phonemes = self.phonetics[token]
        for phoneme in phonemes:
            phoneme_na = self.builder.find_create_assembly(self._append_phoneme_prefix(phoneme))
            phoneme_na.firing_ticks.clear()
            phoneme_na.firing_ticks.append(starting_tick)
            starting_tick += 1
        return starting_tick - 1

    def prepare_phoneme_assemblies(self, starting_tick: int, token: str) -> int:
        # word_na = self.builder.find_create_assembly(token)
        # word_na.firing_ticks.clear()
        # word_na.firing_ticks.append(starting_tick)
        self.builder.build_phonemes_from_word(token, area=self, starting_tick=starting_tick)
        return starting_tick + 1

    @staticmethod
    def _append_phoneme_prefix(pattern):
        return 'ph: ' + pattern

    def build_phonemes_from_text(self, filename: str):
        text_lines = load_list_from_file(filename)
        overall_words = []
        for line in text_lines:
            line = clean_punctuation(line)
            overall_words.extend(line.split())
        for word in overall_words:
            self._build_phonemes_from_word(word)

    def _find_create_syllable_assembly(self, pattern: str, capacity: int = 0) -> NeuralAssembly:
        na = self.builder.find_create_assembly(pattern)
        na.area = self
        na.capacity = capacity
        return na

    def build_phonemes_from_word(self, word: str):
        phonemes = self.phonetics[word]
        word_na = self._find_create_syllable_assembly(word)
        syllables = []
        for i in range(len(phonemes) - 1):
            syllable = f'{phonemes[i]}{phonemes[i+1]}'
            na = self._find_create_syllable_assembly(syllable)
            connection = self.builder.check_create_connection(source=na, target=word_na)
            syllables.append(syllable)

    def build_structure(self):
        text_lines = load_list_from_file(self.agent.config.get('phonetics_path'))
        overall_words = []
        # for line in text_lines:
        #     line = clean_punctuation(line)
        #     overall_words.extend(line.split())
        # for word in overall_words:
        #     self.build_phonemes_from_word(word)

    def on_fire(self, assembly: NeuralAssembly):
        """
        Handles the case when a DOPEd assembly is firing after a previously fired assembly.
        We must get that assembly marked as DOPEd too
        :param na:
        :return:
        """
        self.agent.queue_message('phonological_assembly_fired')
        container = assembly.container
        if assembly.doped:
            other_assemblies = [na for na in container.get_neural_area_assemblies(area=self) if na != assembly]
            for na in other_assemblies:
                if na.last_fired_at >= container.current_tick - 3:
                    na.on_doped(container.current_tick)