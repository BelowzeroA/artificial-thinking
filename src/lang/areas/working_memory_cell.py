from lang.neural_area import NeuralArea


class WorkingMemoryCell(NeuralArea):
    """
     Represents a one-concept-at-a-time storage in the working memory
     """
    def __init__(self, name: str, agent):
        from lang.assembly_builder import AssemblyBuilder
        super().__init__(name, agent)
        self.phonetics = {}
        self.builder: AssemblyBuilder = None
        self.vocal_area: NeuralArea = None
        self.winner_takes_it_all_strategy = True

    def connect_to(self, source_area: NeuralArea):
        self.upstream_areas.append(source_area)

    def before_assemblies_update(self, tick: int):
        pass