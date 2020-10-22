from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea


PROLONGED_FIRING_SPAN = 4


class PhraseRecognitionProjectedArea(NeuralArea):
    """
     Represents all crutches for the zone
     """
    def __init__(self, name: str, agent, zone):
        from lang.neural_assembly import NeuralAssembly
        super().__init__(name, agent, zone)
        self.winner_takes_it_all_strategy = False
        self.allows_assembly_merging = True
        self.allows_projection = True
        self.inhibits_itself = False
        self.use_prolonged_firing = False
        self.prolonged_firing_assembly: NeuralAssembly = None
        self.prolonged_firing_starting_tick = 0
        self.multiplier = 1

    def on_fire(self, na: 'NeuralAssembly'):
        super().on_fire(na)
        inhibited_areas = [a for a in self.agent.container.areas if self in a.inhibiting_areas]
        current_tick = self.agent.environment.current_tick
        target_tick = current_tick + 1
        if current_tick not in na.firing_ticks and self.use_prolonged_firing:
            self.prolonged_firing_assembly = na
            self.prolonged_firing_starting_tick = target_tick

        for area in inhibited_areas:
            area.inhibited_at_ticks.append(target_tick)
        if self.inhibits_itself:
            self.inhibited_at_ticks.append(target_tick)

    def before_assemblies_update(self, tick: int):
        if self.winner_takes_it_all_strategy:
            self.handle_output_area_assemblies()
            self.check_set_is_winner(threshold=HyperParameters.phonetic_recognition_threshold)
            return
        if self.prolonged_firing_assembly is None or not self.use_prolonged_firing:
            return
        assemblies = self.get_assemblies()
        firing_assemblies = [a for a in assemblies if a.potential >= a.threshold]
        if len(firing_assemblies):
            self.prolonged_firing_assembly = None
            self.prolonged_firing_starting_tick = 0
        if self.prolonged_firing_assembly:
            if tick - self.prolonged_firing_starting_tick <= PROLONGED_FIRING_SPAN:
                self.prolonged_firing_assembly.firing_ticks.append(tick)
            else:
                self.prolonged_firing_assembly = None

    def handle_output_area_assemblies(self):
        assemblies = [na for na in self.agent.container.assemblies if na.area == self and na.potential > 0]
        for assembly in assemblies:
            fired_contributors = assembly.fired_contributors
            if len(fired_contributors):
                assembly.potential *= fired_contributors[0].area.multiplier


