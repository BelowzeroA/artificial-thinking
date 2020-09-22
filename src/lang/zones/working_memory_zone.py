from lang.areas.speech_program_selector_area import SpeechProgramSelectorArea
from lang.areas.working_memory_cell import WorkingMemoryCell
from lang.areas.working_memory_comparer_area import WorkingMemoryComparerArea
from lang.neural_zone import NeuralZone


class WorkingMemoryZone(NeuralZone):
    """
    Memorizes several concepts at a time for some period
    Corresponds to the Hippocampus
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.num_units = 5
        self._input_area = None
        self.prepare_areas()

    def prepare_areas(self):
        for i in range(self.num_units):
            cell = WorkingMemoryCell(f'cell_{i}', self.agent)
            self.agent.container.add_area(cell)
            comparer = WorkingMemoryComparerArea(f'comparer_{i}', self.agent)
            comparer.connect_to(cell)
            self.agent.container.add_area(comparer)

    def prepare_assemblies(self, source, tick: int):
        pass

    def before_assemblies_update(self, tick: int):
        return
        for area in self.areas[1:]:
            area.before_assemblies_update(tick)