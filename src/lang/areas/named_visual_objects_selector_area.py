# from lang.areas.visual_lexicon_output_tone_area import VisualLexiconOutputToneArea
from lang.areas.named_visual_objects_output_tone_area import NamedVisualObjectsOutputToneArea
from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly


class NamedVisualObjectsSelectorArea(NeuralArea):
    """
     An output area of NamedVisualObjectsZone
     """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.winner_takes_it_all_strategy = True
        self.allows_assembly_merging = False
        self.allows_projection = True
        self.tone_area = NamedVisualObjectsOutputToneArea.add('tone_output', self.agent, self.zone)

    def before_assemblies_update(self, tick: int):
        assemblies = [na for na in self.agent.container.assemblies if na.area == self and na.potential > 0]
        for assembly in assemblies:
            fired_contributors = assembly.fired_contributors
            if len(fired_contributors):
                upstream_fired_assembly = fired_contributors[0]
                upstream_area = upstream_fired_assembly.area
                assembly.potential += upstream_area.firing_counts[upstream_fired_assembly]
        self.check_set_is_winner(threshold=HyperParameters.phonetic_recognition_threshold)

    def on_fire(self, na: NeuralAssembly):
        self.tone_area.assembly.fire()




