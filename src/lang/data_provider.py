from collections import defaultdict

from lang.assembly_source import AssemblySource
from common.file_ops import load_list_from_file
from lang.configs import SCENARIO_PREFIX
from lang.hyperparameters import HyperParameters

comment_sign = '# '


class DataProvider:

    def __init__(self, filename: str):
        self._items = defaultdict(str)
        self.filename = filename
        self.scenario_length = 0
        self._load_items()

    def _load_items(self):
        lines = load_list_from_file(self.filename)
        episode_counter = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(comment_sign):
                continue
            # colon_ind = line.index(':')
            # index = int(line[:colon_ind])
            # content = line[colon_ind + 1:].strip()
            if line.startswith(SCENARIO_PREFIX):
                continue
            index = episode_counter * HyperParameters.episode_length if episode_counter > 0 else 1
            episode_counter += 1
            self._items[index] = AssemblySource(line)
        self.scenario_length = episode_counter * HyperParameters.episode_length

    def __getitem__(self, i) -> AssemblySource:
        return self._items[i]