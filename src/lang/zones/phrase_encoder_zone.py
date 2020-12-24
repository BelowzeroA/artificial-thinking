from typing import List

from lang.areas.phrase_encoder.phrase_encoder_area import PhraseEncoderArea
from lang.areas.phrase_encoder.phrase_encoder_projected_area import PhraseEncoderProjectedArea
from lang.neural_area import NeuralArea
from lang.neural_zone import NeuralZone
from lang.zones.named_visual_objects_zone import NamedVisualObjectsZone
from lang.zones.phonetic_recognition_zone import PhoneticRecognitionZone


class PhraseEncoderZone(NeuralZone):
    """
    Recognizes phrases consisting of multiple words
    Corresponds to no brain area,
    totally fictional and created to workaround the complexity of phonetic processing in the brain
    """
    def __init__(self, agent: 'Agent'):
        super().__init__(name=type(self).__name__, agent=agent)
        self.short_name = 'PhrEnc'
        self.num_layers = 3
        self.projected_areas: List[PhraseEncoderProjectedArea] = []
        self._input_area = None
        self._output_area = None
        self.prepare_areas()

    def make_layer(self, ind: int):
        area = PhraseEncoderArea.add(f'area_{ind + 1}', self.agent, self)
        if ind > 0:
            area.inhibits_itself = True
        areas = [area]
        for j in range(self.num_layers * 2 - ind - 3):
            projected_area = PhraseEncoderProjectedArea.add(f'proj_area_{ind + 1}_{j + 1}', self.agent, self)
            projected_area.multiplier = ind + 1
            if j == 0:
                projected_area.use_prolonged_firing = True
            prev_area = area if j == 0 else areas[j]
            projected_area.add_exciting_area(prev_area)
            areas.append(projected_area)
        return areas

    def prepare_areas(self):
        self._output_area = PhraseEncoderProjectedArea.add(f'output', self.agent, self)
        self._output_area.allows_assembly_merging = False
        self._output_area.winner_takes_it_all_strategy = True
        layer_areas = []
        for i in range(self.num_layers):
            areas = self.make_layer(i)
            layer_areas.append(areas)
            area_zero = areas[0]
            if i > 0:
                skip_factor = i - 1
                prev_layer_areas = layer_areas[i - 1]
                # for prev_area in prev_layer_areas[2:]:
                #     prev_area.add_inhibiting_area(area_zero)
                for prev_area in prev_layer_areas[:2 + skip_factor: skip_factor + 1]:
                    area_zero.add_exciting_area(prev_area)
                if i > 1:
                    prev_prev_layer_areas = layer_areas[i - 2]
            else:
                self._input_area = area_zero
            last_layer_area = areas[-1:][0]
            self._output_area.add_exciting_area(last_layer_area)
        self._input_area.allows_projection = True

    def output_areas(self):
        return [self._output_area]

    def connect_to(self, pr: PhoneticRecognitionZone):
        for pr_area in pr.output_areas():
            self._input_area.connect_to(pr_area)