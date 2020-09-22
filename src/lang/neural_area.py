from typing import List, Set

# from lang.agent import Agent
from lang.neural_assembly import NeuralAssembly
from lang.primitives.inter_area_message import InterAreaMessage


class NeuralArea:
    """
    Neural area contains neural assemblies and undermines their properties and connectivity with other assemblies
    """
    def __init__(self, name: str, agent: 'Agent', zone: 'NeuralZone'):
        self.id = None
        self.name = name
        self.agent = agent
        self.zone = zone
        self.builder: 'AssemblyBuilder' = self.agent.assembly_builder
        self.modalities = []
        self.exciting_areas: List[NeuralArea] = []
        self.tone_exciting_areas: List[NeuralArea] = []
        self.inhibiting_areas: List[NeuralArea] = []
        self.absorbs_dopamine = False
        self.winner_takes_it_all_strategy = False
        self.double_activation_from: List[NeuralArea] = []
        self.allows_assembly_merging = False
        self.allows_projection = False
        self.sends_tone = False
        self.inhibited_at_ticks = []

    def corresponds_to_prefix(self, prefix: str) -> bool:
        return prefix in self.modalities

    def add_exciting_area(self, area):
        self.exciting_areas.append(area)

    def add_tone_exciting_area(self, area):
        self.tone_exciting_areas.append(area)

    def add_inhibiting_area(self, area):
        self.inhibiting_areas.append(area)

    def connect_to(self, source_area: 'NeuralArea'):
        self.exciting_areas.append(source_area)

    def get_assemblies(self):
        return [a for a in self.agent.container.assemblies if a.area == self]

    def get_projected_areas(self):
        return [area for area in self.agent.container.areas if self in area.exciting_areas and area.allows_projection]

    def get_tone_projected_areas(self):
        return [area for area in self.agent.container.areas
                if self in area.tone_exciting_areas and area.allows_projection]

    @classmethod
    def add(cls, name, agent, zone) -> 'NeuralArea':
        area = cls(name, agent, zone)
        agent.container.add_area(area)
        return area

    def on_fire(self, na: NeuralAssembly):
        """
        reacts on the event of a neural assembly firing
        :param na:
        """
        if self.sends_tone:
            connections = self.agent.container.get_assembly_outgoing_connections(na=self)
            for conn in connections:
                conn.pulsing = True

    def handle_message(self, msg: InterAreaMessage):
        return False

    def allow_firing(self, na: NeuralAssembly):
        """
        Adds additional conditions on whether to fire or not
        :param na:
        :return:
        """
        return True

    def build_structure(self):
        """
        Abstract method to build internal structure
        """
        pass

    def _repr(self):
        return f'[{self.zone}:{self.name}]'

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()
