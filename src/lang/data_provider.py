from collections import defaultdict

from lang.assembly_source import AssemblySource
from common.file_ops import load_list_from_file
from lang.configs import SCENARIO_PREFIX


class DataProvider:

    def __init__(self, filename: str):
        self._items = defaultdict(str)
        self.filename = filename
        self._load_items()

    def _load_items(self):
        lines = load_list_from_file(self.filename)
        for line in lines:
            line = line.strip()
            if not line:
                continue
            colon_ind = line.index(':')
            index = int(line[:colon_ind])
            content = line[colon_ind + 1:].strip()
            if content.startswith(SCENARIO_PREFIX):
                continue
            self._items[index] = AssemblySource(content)

    def __getitem__(self, i) -> AssemblySource:
        return self._items[i]