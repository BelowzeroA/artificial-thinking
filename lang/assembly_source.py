from typing import List


class AssemblySource:
    """
    Represents raw data of a neural assembly
    """
    def __init__(self, source_line: str):
        self.source_line = source_line
        self.visuals: List[str] = []
        self.actions: List[str] = []
        self.observations: List[str] = []
        self.tokens = []
        self.doped = False
        self._parse()

    def _parse(self):
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
        if 'DOPE' in parts:
            self.doped = True
            del parts[parts.index('DOPE')]
        for vis in self.visuals:
            del parts[parts.index(vis)]
        # for action in self.actions:
        #     del parts[parts.index(action)]
        self.tokens = parts