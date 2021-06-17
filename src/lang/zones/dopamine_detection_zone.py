from lang.neural_zone import NeuralZone


class DopamineDetectionZone(NeuralZone):
    """
    Detects pre-dopamine conditions and controls dopamine flow
    Corresponds to the Thalamus
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'DopeDetect'
        self.num_areas = 2
        self.prepare_areas()

    def prepare_areas(self):
        pass

    def connect_to_sensors(self, areas):
        for area in areas:
            for rule_area in self.rules:
                rule_area.add_exciting_area(area)

    def prepare_assemblies(self, source, tick: int):
        pass

    def before_assemblies_update(self, tick: int):
        return