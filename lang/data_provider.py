from collections import defaultdict

from lang.assembly_source import AssemblySource
from utils.file_ops import load_list_from_file


class DataProvider:

    def __init__(self, filename: str):
        self._items = defaultdict(str)
        self.filename = filename
        self._load_items()


    def _load_items(self):
        lines = load_list_from_file(self.filename)
        for line in lines:
            colon_ind = line.index(':')
            index = int(line[:colon_ind])
            self._items[index] = AssemblySource(line[colon_ind + 1:])

    def __getitem__(self, i) -> AssemblySource:
        return self._items[i]