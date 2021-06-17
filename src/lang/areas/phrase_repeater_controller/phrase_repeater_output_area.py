from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly


class PhraseRepeaterOutputArea(NeuralArea):
    """
     Output area for PhraseRepeaterControllerZone
     """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.winner_takes_it_all_strategy = False
        self.allows_assembly_merging = False
        self.allows_projection = True
        self.callbacks = []

    def before_assemblies_update(self, tick: int):
        self.check_set_is_winner(threshold=HyperParameters.phonetic_recognition_threshold)

    def on_fire(self, na: NeuralAssembly):
        for callback in self.callbacks:
            callback(na)


