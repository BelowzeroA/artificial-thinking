from collections import defaultdict

from lang.assembly_source import AssemblySource
from common.file_ops import load_list_from_file
from lang.configs import SCENARIO_PREFIX
from lang.hyperparameters import HyperParameters

comment_sign = '# '
reward_line_prefix = '@dope'
for_loop_prefix = '@for'


class DataProvider:

    def __init__(self, filename: str):
        self._items = {} #defaultdict(str)
        self.filename = filename
        self.scenario_length = 0
        self._current_key_index = 0
        self._load_items()

    def _load_items(self):
        lines = load_list_from_file(self.filename)
        episode_counter = 0
        current_reward_line = None
        current_iter_counter = 1
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(comment_sign):
                continue
            if line.startswith(SCENARIO_PREFIX):
                continue
            if line.startswith(reward_line_prefix):
                current_reward_line = line[len(reward_line_prefix) + 1:]
                continue
            if line.startswith(for_loop_prefix):
                current_iter_counter = self._get_param_in_parenthesis(line)
                continue

            for i in range(current_iter_counter):
                index = episode_counter * HyperParameters.episode_length if episode_counter > 0 else 1
                episode_counter += 1
                self._items[index] = AssemblySource(line, current_reward_line)
            current_reward_line = None
            current_iter_counter = 1
        self.scenario_length = episode_counter * HyperParameters.episode_length

    @staticmethod
    def _get_param_in_parenthesis(line: str):
        opening_parenthesis_pos = line.index('(')
        closing_parenthesis_pos = line.index(')')
        return int(line[opening_parenthesis_pos + 1:closing_parenthesis_pos])

    def __getitem__(self, i) -> AssemblySource:
        return self._items[i] if i in self._items else None

    def __iter__(self):
        self._current_key_index = 0
        return self

    def __next__(self) -> int:
        key_index = self._current_key_index
        if key_index >= len(self._items):
            raise StopIteration
        item = list(self._items.keys())[key_index]
        self._current_key_index += 1
        return item