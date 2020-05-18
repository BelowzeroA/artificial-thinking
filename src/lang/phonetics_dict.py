from typing import List

from common.file_ops import load_list_from_file


class PhoneticsDict:
    """
    Contains phonemes of tokens
    """
    def __init__(self, filename: str):
        self.filename = filename
        self._items = {}
        self._load_items()

    def _load_items(self):
        lines = load_list_from_file(self.filename)
        for line in lines:
            space_ind = line.index(' ')
            word = line[:space_ind]
            phonemes = line[space_ind + 1:].split()
            self._items[word] = phonemes

    def isin(self, word: str) -> bool:
        lowercased_word = word.lower()
        return lowercased_word in self._items

    def __contains__(self, word: str) -> bool:
        lowercased_word = word.lower()
        return lowercased_word in self._items

    def __getitem__(self, word: str) -> List[str]:
        lowercased_word = word.lower()
        assert lowercased_word in self._items, f'"{lowercased_word}" is not in PhoneticsDict'
        return self._items[lowercased_word]