from lang.areas.visual_recognition_area import VisualRecognitionArea
from lang.hyperparameters import HyperParameters
from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly
from lang.zones.visual_recognition_zone import VisualRecognitionZone


class VisualLexiconArea(NeuralArea):
    """
     Represents a single layer in the hierarchy of VisualLexiconZone
     """
    def __init__(self, name: str, agent, zone):
        super().__init__(name, agent, zone)
        self.allows_assembly_merging = True
        self.allows_projection = False
        self.firing_counts = {}

    def on_fire(self, na: NeuralAssembly):
        # Strengthen the connection from visual recognition area
        connections = self.agent.container.get_assembly_incoming_connections(na)
        connections_from_vr = [c for c in connections if isinstance(c.source.area.zone, VisualRecognitionZone)]
        connections_from_vr[0].multiplier = 2
        # Count firing
        if na not in self.firing_counts:
            self.firing_counts[na] = 0
        self.firing_counts[na] += 500 if len(na.fired_contributors) > 1 else 1

