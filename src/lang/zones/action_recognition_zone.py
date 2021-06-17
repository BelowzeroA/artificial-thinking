from lang.areas.action_recognition.action_recognition_area import ActionRecognitionArea
from lang.areas.visual_recognition_area import VisualRecognitionArea
from lang.assembly_source import AssemblySource
from lang.hyperparameters import HyperParameters
from lang.neural_zone import NeuralZone


class ActionRecognitionZone(NeuralZone):
    """
    Recognizes actions of visual objects
    Corresponds to the Inferior Temporal lobe (ITL)
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'AR'
        self.num_areas = 1
        self._input_area: ActionRecognitionArea = None
        self.prepare_areas()

    def output_areas(self):
        return [self._input_area]

    def prepare_areas(self):
        self._input_area = ActionRecognitionArea.add(f'area_{0}', self.agent, self)

    def prepare_assemblies(self, source: AssemblySource, tick: int):
        firing_span = [t + tick for t in range(HyperParameters.episode_length - 5)]
        if source.scene:
            for scene_object in self.scene:
                action_pattern = f'a:{scene_object["action"]}'
                na = self.builder.find_create_assembly(pattern=action_pattern, area=self._input_area)
                na.firing_ticks.extend(firing_span)
