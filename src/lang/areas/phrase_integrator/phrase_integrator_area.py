from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea


class PhraseIntegratorArea(NeuralArea):
    """
     Represents all crutches for the zone
     """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.winner_takes_it_all_strategy = False
        self.allows_assembly_merging = False
        self.allows_projection = True
        self.inhibits_itself = False

    def before_assemblies_update(self, tick: int):
        if self.winner_takes_it_all_strategy:
            return
        assemblies = self.get_assemblies()
        firing_assemblies = [a for a in assemblies if a.potential >= a.threshold]
        if len(firing_assemblies) > 1:
            for assembly in firing_assemblies:
                if not assembly.source_assemblies[0].is_tone:
                    assembly.potential = 0


