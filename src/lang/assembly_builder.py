import itertools
from typing import List
from collections import Counter

from legacy.phonological_memory import PhonologicalMemory
from lang.assembly_source import AssemblySource
from lang.connection import Connection
from lang.data_provider import DataProvider
from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly
from lang.phonetics_dict import PhoneticsDict
from common.file_ops import load_list_from_file
from common.misc import clean_punctuation


PERCEPTUAL_PREFIXES = ['ph', 'v']
LINKED_PREFIX = 'lnk'


class AssemblyBuilder:
    """
    Builds and manipulates neural assemblies and connections
    """
    def __init__(self, agent: 'Agent', data_provider: DataProvider):
        self.agent = agent
        self.data_provider = data_provider
        self.container = agent.container
        self.phonetics = PhoneticsDict(agent.config.get('phonetics_path'))

    def get_assembly_source(self, tick: int):
        return self.data_provider[tick]

    def prepare_assemblies(self, tick: int):
        if not self.data_provider[tick]:
            return
        assembly_source = self.data_provider[tick]
        visual_nas = self._check_create_visual_assemblies(assembly_source)
        total_ticks = 0
        last_observation = None
        current_planned_tick = tick
        for token in assembly_source.tokens:
            if token in assembly_source.actions:
                current_planned_tick = self._check_create_action_assembly(
                    pattern=token,
                    firing_tick=current_planned_tick
                )
            elif token in assembly_source.observations:
                last_observation = self._check_create_observation_assembly(
                    pattern=token,
                    firing_tick=current_planned_tick
                )
            elif token == 'DOPE':
                last_observation.doped = True
                continue
            else:
                # it's a phonetic token
                current_planned_tick = \
                    self.container.phonological_memory.prepare_phoneme_assemblies(current_planned_tick, token)
            current_planned_tick += 1
        for na in visual_nas:
            na.firing_ticks = list(range(tick, current_planned_tick + 3))

    def _prepare_phoneme_assemblies(self, starting_tick: int, phonemes: List[str]) -> int:
        for phoneme in phonemes:
            phoneme_na = self.find_create_assembly(self._append_phoneme_prefix(phoneme))
            phoneme_na.firing_ticks.clear()
            phoneme_na.firing_ticks.append(starting_tick)
            starting_tick += 1
        return starting_tick - 1

    def _check_create_visual_assemblies(self, source: AssemblySource) -> List[NeuralAssembly]:
        visual_nas: List[NeuralAssembly] = []
        for pattern in source.visuals:
            visual_na = self.find_create_assembly(pattern=pattern)
            visual_nas.append(visual_na)
        return visual_nas

    def _check_create_action_assembly(self, pattern: str, firing_tick: int) -> NeuralAssembly:
        na = self.find_create_assembly(pattern=pattern)
        na.firing_ticks = [firing_tick + tick for tick in range(HyperParameters.action_firing_span)]
        # if not na.doped:
        #     na.doped = doped
        # self._create_linked_assembly(source_na=na, capacity=1)
        return na.firing_ticks[-1:][0]

    def _check_create_observation_assembly(self, pattern: str, firing_tick: int) -> NeuralAssembly:
        na = self.find_create_assembly(pattern=pattern)
        na.firing_ticks = [firing_tick + tick for tick in range(HyperParameters.observation_firing_span)]
        return na

    def _build_assemblies_for_token(self, token: str):
        token_assembly = self._find_create_assembly(token)
        phonemes = self.phonetics.items[token]
        for phoneme in phonemes:
            self.find_create_assembly(phoneme)

    def _create_joint_assembly(self, nas: List[NeuralAssembly], area: NeuralArea) -> NeuralAssembly:
        pattern = self._make_joint_pattern(nas)
        max_level_na = max(nas, key=lambda na: na.hierarchy_level)
        joint_na = self.find_create_assembly(pattern, area=area)
        # joint_na.capacity = self._get_joint_capacity(nas)
        joint_na.is_joint = True
        joint_na.hierarchy_level = max_level_na.hierarchy_level + 1
        return joint_na

    @staticmethod
    def _make_joint_pattern(nas: List[NeuralAssembly]) -> str:
        nas_priorities = []
        for na in nas:
            priority = 0 if na.area.allows_projection else 1
            nas_priorities.append((na, priority))
        nas_priorities.sort(key=lambda x: x[1])
        patterns = [t[0].cleaned_pattern for t in nas_priorities]
        cleaned_patterns = []
        for i in range(len(patterns) - 1):
            curr_pattern = patterns[i]
            next_pattern = patterns[i + 1]
            if '+' in curr_pattern:
                last_curr_symbol = curr_pattern.split('+')[-1:][0].strip()
                next_pattern_parts = next_pattern.split('+')
                first_next_symbol = next_pattern_parts[0].strip()
                if last_curr_symbol == first_next_symbol:
                    next_pattern = '+'.join(next_pattern_parts[1:])
                cleaned_patterns.extend([curr_pattern, next_pattern])
            else:
                cleaned_patterns.extend([curr_pattern, next_pattern])
        pattern = '+'.join(cleaned_patterns)
        return pattern

    def find_create_assembly(self, pattern: str, area: NeuralArea) -> NeuralAssembly:
        na = self.container.get_assembly_by_pattern(pattern, area)
        if not na:
            na = self.container.create_assembly(pattern)
            prefix = self._get_pattern_prefix(pattern)
            if area is None:
                area = self.container.get_area_by_prefix(prefix)
            if area is None:
                raise ValueError(f'No area found for prefix "{prefix}"')
            na.area = area
            if prefix in PERCEPTUAL_PREFIXES:
                na.perceptual = True
                # na.capacity = HyperParameters.initial_receptive_assembly_capacity
        return na

    @staticmethod
    def _get_pattern_prefix(pattern: str) -> str:
        if pattern.startswith(LINKED_PREFIX):
            pattern = pattern[len(LINKED_PREFIX) + 1:]
        if ':' in pattern:
            return pattern[:pattern.index(':')]
        return None

    # def _find_create_assembly_chain(self, pattern: str, area: NeuralArea, capacity: int) -> NeuralAssembly:
    #     na = self.find_create_assembly(pattern, area)
    #     na.capacity = capacity
    #     if na.area.create_linked_assembly:
    #         linked_capacity = na.capacity // HyperParameters.linked_assembly_capacity_rate
    #         hier_level = na.hierarchy_level - 1
    #         if hier_level <= 0:
    #             hier_level = 1
    #         linked_capacity = linked_capacity // hier_level
    #         if linked_capacity >= HyperParameters.minimal_capacity:
    #             self._create_linked_assembly(source_na=na, capacity=linked_capacity)
    #     return na

    def _create_projected_assembly(self, source_na: NeuralAssembly, area: NeuralArea) -> NeuralAssembly:
        na = self.find_create_assembly(source_na.pattern, area=area)
        # linked1.fill_contributors([source_na])
        connection = self.check_create_connection(source=source_na, target=na)
        connection.multiplier = 2
        return na

    def check_create_connection(self, source: NeuralAssembly, target: NeuralAssembly) -> Connection:
        connection = self.container.get_connection_between_nodes(source=source, target=target)
        if not connection:
            connection = self.container.create_connection(source=source, target=target)
        return connection

    def _find_linked_assembly(self, na: NeuralAssembly) -> NeuralAssembly:
        return self.container.get_assembly_by_pattern(f'{LINKED_PREFIX}:{na.pattern}')

    def build_phonemes_from_text(self, filename: str):
        text_lines = load_list_from_file(filename)
        overall_words = []
        for line in text_lines:
            line = clean_punctuation(line)
            overall_words.extend(line.split())
        for word in overall_words:
            self.build_phonemes_from_word(word)

    # def build_phonemes_from_word_old(self, word: str, area, starting_tick: int):
    #     build_chain = False
    #     firing_count = HyperParameters.phonological_na_firing_count
    #     if word in self.phonetics:
    #         phonemes = self.phonetics[word]
    #         if len(phonemes) > 1:
    #             build_chain = True
    #         else:
    #             word = phonemes[0]
    #
    #     if build_chain:
    #         for i in range(len(phonemes) - 1):
    #             firing_ticks1 = [tick for tick in range(starting_tick + i, starting_tick + i + firing_count)]
    #             na1 = self._find_create_assembly_chain(
    #                 pattern=self._append_phoneme_prefix(phonemes[i]),
    #                 area=area,
    #                 capacity=HyperParameters.initial_receptive_assembly_capacity)
    #
    #             na1.firing_ticks.extend(firing_ticks1)
    #             na1_linked = self._find_linked_assembly(na1)
    #             na2 = self._find_create_assembly_chain(
    #                 pattern=self._append_phoneme_prefix(phonemes[i + 1]),
    #                 area=area,
    #                 capacity=HyperParameters.initial_receptive_assembly_capacity)
    #             firing_ticks2 = [tick for tick in range(starting_tick + i + 1, starting_tick + i + 1 + firing_count)]
    #             na2.firing_ticks.extend(firing_ticks2)
    #
    #             combined_pattern = phonemes[i] + phonemes[i + 1]
    #             combined_capacity = self._get_joint_capacity([na1_linked, na2])
    #             combined_assembly = self._find_create_assembly_chain(
    #                 pattern=combined_pattern,
    #                 area=area,
    #                 capacity=combined_capacity)
    #             combined_assembly.fill_contributors([na1, na1_linked, na2])
    #             combined_assembly.is_combined = True
    #             self.check_create_connection(source=na1_linked, target=combined_assembly)
    #             self.check_create_connection(source=na2, target=combined_assembly)
    #     else:
    #         na = self._find_create_assembly_chain(
    #             pattern=self._append_phoneme_prefix(word),
    #             area=area,
    #             capacity=HyperParameters.initial_receptive_assembly_capacity)
    #         firing_ticks = [tick for tick in range(starting_tick, starting_tick + firing_count)]
    #         na.firing_ticks = firing_ticks
    #         # self._create_linked_assembly(source_na=na, capacity=HyperParameters.initial_receptive_assembly_capacity)

    def build_phonemes_from_word(self, word: str, area, starting_tick: int):
        firing_count = HyperParameters.phonological_na_firing_count
        if word in self.phonetics:
            phonemes = self.phonetics[word]
        else:
            raise ValueError(f'word "{word}" is not in the phonetics dictionary')
        for i in range(len(phonemes)):
            firing_ticks1 = [tick for tick in range(starting_tick + i, starting_tick + i + firing_count)]
            na1 = self.find_create_assembly(pattern=self._append_phoneme_prefix(phonemes[i]), area=area)
            na1.firing_ticks.extend(firing_ticks1)
        return starting_tick + len(phonemes)

    @staticmethod
    def _append_phoneme_prefix(pattern):
        return 'ph: ' + pattern

    def _get_joint_assembly(self, nas: List[NeuralAssembly]) -> NeuralAssembly:
        """
        Returns a common downstream assembly
        :param nas: source assemblies
        :return:
        """
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
            # if all fired assemblies are perceptual, don't make a joint assembly
            perceptual = [na for na in fired_assemblies if na.perceptual]
            if len(perceptual) == len(fired_assemblies) and False:
                return
            combinations = list(itertools.combinations(fired_assemblies, 2))
            for combination in combinations:
                combination = list(combination)
                # checking the situation when a common downstream assembly for currently fired assemblies already exists
                downstream_assembly_existed = self._check_update_downstream_assembly(combination)
                if downstream_assembly_existed:
                    continue
                joint_area = self._get_common_projected_area(combination)
                if joint_area and joint_area.allows_assembly_merging:
                    joint_na = self._create_joint_assembly(combination, joint_area)
                    joint_na.formed_at = self.container.current_tick
                    # joint_na.fill_contributors(combination)
                    for na in combination:
                        self.check_create_connection(na, joint_na)
                    # self._create_linked_assembly(joint_na, capacity=joint_capacity)
                    print(f'area {joint_area} joint assembly {joint_na} created')

    def _get_common_projected_area(self, fired_assemblies: List[NeuralAssembly]) -> NeuralArea:
        areas = set([a.area for a in fired_assemblies])
        for area in self.container.areas:
            if areas.issubset(set(area.exciting_areas)):
                return area
        return None

    def _check_update_downstream_assembly(self, fired_assemblies: List[NeuralAssembly]) -> bool:
        downstream_assembly = self._get_downstream_assembly(fired_assemblies)
        if downstream_assembly:
            for na in fired_assemblies:
                if self._assemblies_can_be_connected(na, downstream_assembly):
                    self.check_create_connection(na, downstream_assembly)
                    if na not in downstream_assembly.contributors:
                        downstream_assembly.contributors.append(na)
        return downstream_assembly is not None

    @staticmethod
    def _assemblies_can_be_connected(source: NeuralAssembly, target: NeuralAssembly) -> bool:
        return source.area in target.area.exciting_areas

    def _build_linked_assemblies(self):
        """
        builds linked assemblies if necessary.
        Linked assembly is an assembly that fires one tick later after a master assembly
        :return:
        """
        fired_assemblies = [na for na in self.container.assemblies if na.fired]
        for na in fired_assemblies:
            connected_assemblies = [conn.target for conn in self.container.get_assembly_outgoing_connections(na)]
            projected_areas = na.area.get_projected_areas()
            for projected_area in projected_areas:
                already_connected = [assembly for assembly in connected_assemblies if assembly.area == projected_area]
                if already_connected:
                    continue
                self._create_projected_assembly(source_na=na, area=projected_area)

    def build_new_assemblies(self):
        self._build_linked_assemblies()
        self._build_joint_assemblies()

    def prebuild_assemblies(self, phonological_memory: PhonologicalMemory, filename: str):
        text_lines = load_list_from_file(filename)
        overall_words = []
        for line in text_lines:
            line = clean_punctuation(line)
            overall_words.extend(line.split())
        for word in overall_words:
            phonological_memory.build_phonemes_from_word(word)



