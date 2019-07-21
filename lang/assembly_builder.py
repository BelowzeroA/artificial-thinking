from typing import List
from collections import Counter

from lang.assembly_source import AssemblySource
from lang.connection import Connection
from lang.data_provider import DataProvider
from lang.hyperparameters import HyperParameters
from lang.network import Network
from lang.neural_assembly import NeuralAssembly
from lang.phonetics_dict import PhoneticsDict
from neurons.neuro_container import NeuroContainer
from utils.file_ops import load_list_from_file
from utils.misc import clean_punctuation


PERCEPTUAL_PREFIXES = ['ph', 'v']

class AssemblyBuilder:
    """
    Builds and manipulates neural assemblies and connections
    """
    def __init__(self, container: NeuroContainer, data_provider: DataProvider, phonetics: PhoneticsDict):
        self.data_provider = data_provider
        self.container = container
        self.phonetics = phonetics

    def prepare_assemblies(self, tick: int):
        if not self.data_provider[tick]:
            return
        assembly_source = self.data_provider[tick]
        visual_nas = self._check_create_visual_assemblies(assembly_source)
        total_ticks = 0
        current_planned_tick = tick
        for token in assembly_source.tokens:
            if token in assembly_source.actions:
                current_planned_tick = self._check_create_action_assembly(
                    pattern=token,
                    firing_tick=current_planned_tick,
                    doped=assembly_source.doped
                )
            elif token in assembly_source.observations:
                self._check_create_observation_assembly(
                    pattern=token,
                    firing_tick=current_planned_tick,
                    doped=assembly_source.doped
                )
            else:
                phonemes = self.phonetics[token]
                current_planned_tick = self._prepare_phoneme_assemblies(current_planned_tick, phonemes)
            current_planned_tick += 1
        for na in visual_nas:
            na.firing_ticks = list(range(tick, current_planned_tick + 3))

    def _prepare_phoneme_assemblies(self, starting_tick: int, phonemes: List[str]) -> int:
        for phoneme in phonemes:
            phoneme_na = self._find_create_assembly(self._append_phoneme_prefix(phoneme))
            phoneme_na.firing_ticks.clear()
            phoneme_na.firing_ticks.append(starting_tick)
            starting_tick += 1
        return starting_tick - 1

    def _check_create_visual_assemblies(self, source: AssemblySource) -> List[NeuralAssembly]:
        visual_nas: List[NeuralAssembly] = []
        for pattern in source.visuals:
            visual_na = self._find_create_assembly(pattern=pattern)
            visual_nas.append(visual_na)
        return visual_nas

    def _check_create_action_assembly(self, pattern: str, firing_tick: int, doped: bool) -> NeuralAssembly:
        na = self._find_create_assembly(pattern=pattern)
        na.firing_ticks = [firing_tick + tick for tick in range(HyperParameters.action_firing_span)]
        if not na.doped:
            na.doped = doped
        self._create_linked_assembly(source_na=na, capacity=1)
        return na.firing_ticks[-1:][0]

    def _check_create_observation_assembly(self, pattern: str, firing_tick: int, doped: bool) -> NeuralAssembly:
        na = self._find_create_assembly(pattern=pattern)
        na.firing_ticks = [firing_tick + tick for tick in range(HyperParameters.observation_firing_span)]
        if not na.doped:
            na.doped = doped

    def _build_assemblies_for_token(self, token: str):
        token_assembly = self._find_create_assembly(token)
        phonemes = self.phonetics.items[token]
        for phoneme in phonemes:
            self._find_create_assembly(phoneme)

    def _create_joint_assembly(self, nas: List[NeuralAssembly]) -> NeuralAssembly:
        pattern = ''
        for na in nas:
            pattern += f'{na.cleaned_pattern}+'
        pattern = pattern[:-1].strip()
        max_level_na = max(nas, key=lambda na: na.hierarchy_level)
        joint_na = self._find_create_assembly(pattern)
        joint_na.capacity = self._get_joint_capacity(nas)
        joint_na.is_joint = True
        joint_na.hierarchy_level = max_level_na.hierarchy_level + 1
        return joint_na

    def _find_create_assembly(self, pattern: str) -> NeuralAssembly:
        na = self.container.get_assembly_by_pattern(pattern)
        if not na:
            na = self.container.create_assembly(pattern)
            prefix = self._get_pattern_prefix(pattern)
            if prefix in PERCEPTUAL_PREFIXES:
                na.perceptual = True
                na.capacity = HyperParameters.initial_receptive_assembly_capacity
        return na

    @staticmethod
    def _get_pattern_prefix(pattern: str) -> str:
        if ':' in pattern:
            return pattern[:pattern.index(':')]
        return None

    def _find_create_assembly_chain(self, pattern: str, capacity: int) -> NeuralAssembly:
        na = self._find_create_assembly(pattern)
        na.capacity = capacity
        linked_capacity = na.capacity // HyperParameters.linked_assembly_capacity_rate
        hier_level = na.hierarchy_level - 1
        if hier_level <= 0:
            hier_level = 1
        linked_capacity = linked_capacity // hier_level
        if linked_capacity >= HyperParameters.minimal_capacity:
            self._create_linked_assembly(source_na=na, capacity=linked_capacity)
        return na

    def _create_linked_assembly(self, source_na: NeuralAssembly, capacity: int) -> NeuralAssembly:
        linked1 = self._find_create_assembly('lnk1:' + source_na.pattern)
        linked1.perceptual = source_na.perceptual
        linked1.is_link = True
        linked1.capacity = capacity
        linked1.fill_contributors([source_na])
        connection = self._check_create_connection(source=source_na, target=linked1)
        connection.multiplier = 2
        return linked1

    def _check_create_connection(self, source: NeuralAssembly, target: NeuralAssembly) -> Connection:
        connection = self.container.get_connection_between_nodes(source=source, target=target)
        if not connection:
            connection = self.container.create_connection(source=source, target=target)
        return connection

    def _find_linked_assembly(self, na: NeuralAssembly) -> NeuralAssembly:
        return self.container.get_assembly_by_pattern('lnk1:' + na.pattern)

    def build_phonemes_from_text(self, filename: str):
        text_lines = load_list_from_file(filename)
        overall_words = []
        for line in text_lines:
            line = clean_punctuation(line)
            overall_words.extend(line.split())
        for word in overall_words:
            self._build_phonemes_from_word(word)

    def _build_phonemes_from_word(self, word: str):
        phonemes = self.phonetics[word]
        for i in range(len(phonemes) - 1):
            na1 = self._find_create_assembly_chain(pattern=self._append_phoneme_prefix(phonemes[i]),
                                                   capacity=HyperParameters.initial_receptive_assembly_capacity)
            na1_linked = self._find_linked_assembly(na1)
            na2 = self._find_create_assembly_chain(pattern=self._append_phoneme_prefix(phonemes[i + 1]),
                                                   capacity=HyperParameters.initial_receptive_assembly_capacity)
            combined_pattern = phonemes[i] + phonemes[i + 1]
            combined_capacity = self._get_joint_capacity([na1_linked, na2])
            combined_assembly = self._find_create_assembly_chain(pattern=combined_pattern, capacity=combined_capacity)
            combined_assembly.fill_contributors([na1, na1_linked, na2])
            combined_assembly.is_combined = True
            self._check_create_connection(source=na1_linked, target=combined_assembly)
            self._check_create_connection(source=na2, target=combined_assembly)

    @staticmethod
    def _append_phoneme_prefix(pattern):
        return 'ph: ' + pattern

    def _get_joint_assembly(self, nas: List[NeuralAssembly]) -> NeuralAssembly:
        nas_set = set(nas)
        connections = [conn for conn in self.container.connections if conn.source in nas and conn.target.is_joint]
        targets = set([conn.target for conn in connections])
        for target in targets:
            connections_to_target = [conn for conn in connections if conn.target == target]
            source_nas = set([conn.source for conn in connections_to_target])
            if source_nas == nas_set:
                return target
        return None

    @staticmethod
    def _get_joint_capacity(ans: List[NeuralAssembly]) -> int:
        sum = 0
        for an in ans:
            sum += an.capacity
        return sum // len(ans)
        min_capacity = min(cap1, cap2)
        return int(min_capacity / HyperParameters.joint_capacity_denominator)

    def _get_fired_assemblies(self):
        fired_assemblies: List[NeuralAssembly] = [na for na in self.container.assemblies if na.fired]
        lateral_assemblies = set()
        for na in fired_assemblies:
            for contributor in na.contributors:
                if contributor in fired_assemblies:
                    lateral_assemblies.add(contributor)
        for na in lateral_assemblies:
            del fired_assemblies[fired_assemblies.index(na)]
        return fired_assemblies

    def _get_downstream_assembly(self, nas: List[NeuralAssembly]) -> NeuralAssembly:
        outgoing_connections = [conn for conn in self.container.connections if conn.source in nas]
        downstream_assemblies = [conn.target for conn in outgoing_connections if conn.target.is_joint]
        if not downstream_assemblies:
            return None
        counter = Counter(downstream_assemblies)
        most_common = counter.most_common(1)[0][0]
        incoming_connections = [conn for conn in outgoing_connections if conn.target == most_common]
        if len(incoming_connections) > 1:
            if most_common.threshold > 2 and len(nas) == 3:
                return None
            return most_common
        return None

    def _build_joint_assemblies(self):
        fired_assemblies = self._get_fired_assemblies()
        if len(fired_assemblies) > 1:
            if self._get_joint_assembly(fired_assemblies):
                return
            # checking the situation when a common downstream assembly for currently fired assemblies already exists
            downstream_assembly_existed = self._check_update_downstream_assembly(fired_assemblies)
            if downstream_assembly_existed:
                return
            # if all fired assemblies are perceptual, don't make a joint assembly
            perceptual = [na for na in fired_assemblies if na.perceptual]
            if len(perceptual) == len(fired_assemblies):
                return
            joint_capacity = self._get_joint_capacity(fired_assemblies)
            if joint_capacity >= HyperParameters.minimal_capacity:
                joint_na = self._create_joint_assembly(fired_assemblies)
                joint_na.formed_at = self.container.current_tick
                joint_na.fill_contributors(fired_assemblies)
                for na in fired_assemblies:
                    self._check_create_connection(na, joint_na)

    def _check_update_downstream_assembly(self, fired_assemblies: List[NeuralAssembly]) -> bool:
        downstream_assembly = self._get_downstream_assembly(fired_assemblies)
        if downstream_assembly:
            for na in fired_assemblies:
                self._check_create_connection(na, downstream_assembly)
                if na not in downstream_assembly.contributors:
                    downstream_assembly.contributors.append(na)
        return downstream_assembly is not None

    def _build_linked_assemblies(self):
        fired_assemblies = [na for na in self.container.assemblies if na.fired and not na.perceptual and not na.is_link]
        for na in fired_assemblies:
            linked_na = self._find_linked_assembly(na)
            if linked_na:
                continue
            linked_capacity = na.capacity // HyperParameters.linked_assembly_capacity_rate
            hier_level = na.hierarchy_level - 1
            if hier_level <= 0:
                hier_level = 1
            linked_capacity = linked_capacity // hier_level
            if linked_capacity >= HyperParameters.minimal_capacity:
                self._create_linked_assembly(source_na=na, capacity=linked_capacity)

    def build_new_assemblies(self):
        self._build_linked_assemblies()
        self._build_joint_assemblies()




