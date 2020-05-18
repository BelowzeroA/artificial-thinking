from lang.neural_area import NeuralArea


class WorkingMemoryComparerArea(NeuralArea):
    """
     Compares the current input with a corresponding cell value and tonically fires if the values are equal
     """
    def __init__(self, name: str, agent):
        from lang.assembly_builder import AssemblyBuilder
        super().__init__(name, agent)
        self.phonetics = {}
        self.builder: AssemblyBuilder = None

    def connect_to(self, source_area: NeuralArea):
        self.upstream_areas.append(source_area)

    def before_assemblies_update(self, tick: int):
        pass