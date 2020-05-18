from lang.assembly_source import AssemblySource


class NeuralZone:
    """
    Neural zone implements some cognitive function. Consists of several neural areas
    """
    def __init__(self, name: str, agent: 'Agent'):
        self.name = name
        self.agent: 'Agent' = agent
        self.builder: 'AssemblyBuilder' = self.agent.assembly_builder

    def prepare_assemblies(self, source: AssemblySource, tick: int):
        pass

    def before_assemblies_update(self, tick: int):
        pass