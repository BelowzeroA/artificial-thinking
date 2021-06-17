import json
from typing import List


KEY_DOPED = 'DOPE'


class AssemblySource:
    """
    Represents raw data of a neural assembly
    """
    def __init__(self, source_line: str, reward_line: str):
        self.source_line = source_line.strip()
        self.scene = None
        self.visuals: List[str] = []
        self.actions: List[str] = []
        self.observations: List[str] = []
        self.words: List[str] = []
        self.patterns_to_be_rewarded = [p.strip() for p in reward_line.split(',')] if reward_line else None
        self.tokens = []
        self._parse()

    def _parse(self):
        if self.source_line.startswith('['):
            scene_piece = self.source_line[:self.source_line.rfind(']') + 1]
            self.scene = json.loads(scene_piece)
            self.source_line = self.source_line[len(scene_piece) + 1:].strip()
        parts = self.source_line.split()
        for part in parts:
            if part.startswith('v:'):
                self.visuals.append(part)
        for part in parts:
            if part.startswith('a:'):
                self.actions.append(part)
        for part in parts:
            if part.startswith('o:'):
                self.observations.append(part)
        for part in parts:
            if ':' not in part:
                self.words.append(part)
        for vis in self.visuals:
            del parts[parts.index(vis)]
        self.tokens = parts