from lang.neural_area import NeuralArea
from lang.neural_assembly import NeuralAssembly


class DopamineSwitcherArea(NeuralArea):

    def on_fire(self, assembly: NeuralAssembly):
        """
        Handles the case when a DOPEd assembly is firing after a previously fired assembly.
        We must get that assembly marked as DOPEd too
        :param na:
        :return:
        """
        container = assembly.container
        if assembly.doped:
            other_assemblies = [na for na in container.get_neural_area_assemblies(area=self) if na != assembly]
            for na in other_assemblies:
                if na.last_fired_at >= container.current_tick - 3:
                    na.on_doped(container.current_tick)