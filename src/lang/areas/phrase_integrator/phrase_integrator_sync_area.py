from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea


class PhraseIntegratorSyncArea(NeuralArea):
    """
    Delay on the input channel
    """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.allows_projection = True
        self.delay = 1
        self.passing_assemblies = {}

    def before_assemblies_update(self, tick: int):
        assemblies = self.get_assemblies()
        reactivated_assembly = None
        if tick in self.passing_assemblies:
            reactivated_assembly = self.passing_assemblies[tick]
            reactivated_assembly.potential = reactivated_assembly.threshold

        firing_assemblies = [a for a in assemblies if a.potential >= a.threshold]
        for assembly in firing_assemblies:
            # check if the assembly has just been artificially fired by the area
            if assembly != reactivated_assembly:
                # extinguish the current assembly and postpone its firing
                assembly.potential = 0
                self.passing_assemblies[tick + self.delay] = assembly
