import importlib

from typing import List

from common.file_ops import path_from_root
from lang.neural_area import NeuralArea
from lang.primitives.inter_area_message import InterAreaMessage
from lang.zones.phonetic_recognition_zone import PhoneticRecognitionZone
from lang.zones.semantic_storage_zone import SemanticStorageZone
from lang.zones.speech_controller_zone import SpeechControllerZone
from lang.zones.syntax_production_zone import SyntaxProductionZone
from lang.zones.thought_controller_zone import ThoughtControllerZone
from lang.zones.visual_recognition_zone import VisualRecognitionZone
from common.json_serializer import json_serialize
from lang.data_provider import DataProvider
from lang.environment import Environment
from neurons.neuro_container import NeuroContainer


class Agent:
    """
    A baby-learner agent
    """
    def __init__(self, environment: Environment, **kwargs):
        from lang.assembly_builder import AssemblyBuilder
        self.config = kwargs
        self.container = NeuroContainer(self)

        self.container.network = self
        dp = DataProvider(environment.filename)
        self.assembly_builder = AssemblyBuilder(agent=self, data_provider=dp)
        self.samples = []
        # self.current_tick = 0
        self.num_epochs = 0
        self.environment = environment
        self.loop_ended = False
        self._gaba_release = False
        self._gaba_release_start_tick = 0
        self._messages = []
        self.init_zones()
        # self.init_areas()

    @property
    def gaba_release(self):
        """
        Current state of GABA release
        If True, on_negative_reward neurons may fire
        :return:
        """
        return self._gaba_release

    @gaba_release.setter
    def gaba_release(self, val):
        if not self._gaba_release and val:
            self._gaba_release_start_tick = self.current_tick
        self._gaba_release = val

    def reset(self):
        # self.current_tick = 0
        self.container.current_tick = 0

    def queue_message(self, msg_name: str, data: dict = None):
        msg = InterAreaMessage(msg_name)
        msg.data = data
        self._messages.append(msg)

    def update(self):
        self.queue_message('on_tick_beginning')
        self.load_assemblies()
        self._update_state()
        self._update_weights()

    def run(self, max_ticks=10):
        self.loop_ended = False
        result = False
        self.current_tick = 0
        self.container.current_tick = 0
        while self.current_tick <= max_ticks and not self.loop_ended:
            self.current_tick += 1
            self.container.current_tick = self.current_tick
            self.load_assemblies()
            print('Tick {}'.format(self.current_tick))
            self._update_state()
            self._update_weights()
        return result

    def _handle_message_queue(self):
        messages_to_delete = []
        for msg in self._messages:
            handled = False
            for area in self.container.areas:
                handled = area.handle_message(msg)
                if handled:
                    messages_to_delete.append(msg)
                    break
        self._messages.clear()

    def load_assemblies0(self):
        self.assembly_builder.prepare_assemblies(self.environment.current_tick)

    def load_assemblies(self):
        current_tick = self.environment.current_tick
        assembly_source = self.assembly_builder.get_assembly_source(current_tick)
        if assembly_source:
            for zone in self.container.zones:
                zone.prepare_assemblies(assembly_source, current_tick)

    def _update_state(self):
        self._handle_message_queue()

        for zone in self.container.zones:
            zone.before_assemblies_update(self.environment.current_tick)

        for na in self.container.assemblies:
            na.update(self.environment.current_tick)

        for conn in self.container.connections:
            conn.update()

        self._handle_message_queue()

        self.assembly_builder.build_new_assemblies()

        self._check_run_dopamine_flood()

        self._report_fired_assemblies()

    def _check_run_dopamine_flood(self):
        doped_assemblies = [na for na in self.container.assemblies if na.fired and na.doped]
        not_doped_assemblies = [na for na in self.container.assemblies if na.fired and not na.doped]
        if doped_assemblies:
            for na in not_doped_assemblies:
                if na.area.absorbs_dopamine:
                    na.on_doped(self.current_tick)

    def _update_weights(self):
        for neuron in self.container.neurons:
            neuron.update_weights()

    def _report_fired_assemblies(self):
        for na in self.container.assemblies:
            if na.fired:
                print(f'area {na.area} assembly {na} fired')

    def fire_input(self, sample):
        for nrn in sample['input']:
            neuron = self.container.get_neuron_by_id(nrn)
            neuron.initial = True
            neuron.fire()

    def save_model(self, filename):
        out_val = {'neurons': self.container.neurons,
                   'synapses': self.container.synapses}
        with open(filename, mode='wt', encoding='utf-8') as output_file:
            print(json_serialize(out_val), file=output_file)

    def get_state(self):
        repr = ' '.join([str(neuron) for neuron in self.container.neurons])
        return '{}: {}'.format(str(self.current_tick), repr)

    def clear_state(self):
        for neuron in self.container.neurons:
            neuron.potential = 0
            neuron.history.clear()
        for synapse in self.container.synapses:
            synapse.pulsing = False
        for sab in self.container.sabs:
            sab.history.clear()

    def _add_area(self, name: str,
                  modalities: List[str] = None,
                  upstream_areas: List[NeuralArea] = None,
                  create_linked_assembly=True,
                  area_class_name=None):
        if area_class_name:
            pyclass = area_class_name.split('.')[-1]
            module = '.'.join(area_class_name.split('.')[:-1])
            area_class = getattr(importlib.import_module(module), pyclass)
            area = area_class(name, agent=self)
        else:
            area = NeuralArea(name, agent=self)
        self.container.add_area(area)
        if modalities:
            area.modalities = modalities
        if upstream_areas:
            area.upstream_areas = upstream_areas
        area.create_linked_assembly = create_linked_assembly
        return area

    def init_areas(self):
        sensory_na = self._add_area('sensory', ['v', 'o'])

        sensory_joint = self._add_area('sensory joint', None, [sensory_na], False)

        actions_na = self._add_area('actions', ['a'])

        phonological_memory = self._add_area(
            'phonological memory',
            ['ph'],
            upstream_areas=[],
            create_linked_assembly=True,
            area_class_name='lang.areas.phonological_memory.PhonologicalMemory'
        )

        actions_observations = self._add_area(
            'actions with observations',
            None,
            upstream_areas=[sensory_joint, actions_na],
            create_linked_assembly=False,
            area_class_name='lang.areas.dopamine_switcher_area.DopamineSwitcherArea'
        )
        actions_observations.double_activation_from.append(sensory_joint)
        actions_observations.absorbs_dopamine = True

        actions_na.double_activation_from.append(actions_observations)

        vocal_area = self._add_area(
            'Vocal area',
            None,
            upstream_areas=[],
            create_linked_assembly=False,
            area_class_name='lang.areas.vocal_area.VocalArea'
        )

        phonological_memory.vocal_area = vocal_area

        default_na = self._add_area('default')

        self.container.default_area = default_na
        self.container.phonological_memory = phonological_memory
        self.container.vocal_area = vocal_area

        data_dir = path_from_root('data/lang')
        # assembly_builder = AssemblyBuilder(container=container, data_provider=dp, phonetics=phonetics_dict)
        # assembly_builder = AssemblyBuilder(container=self.container, data_provider=dp)
        # assembly_builder.build_phonemes_from_text(os.path.join(data_dir, 'phonetics_learning.txt'))
        self.container.phonological_memory.builder = self.assembly_builder

        # phonetics_path = os.path.join(data_dir, 'phonetics_learning.txt')
        # self.assembly_builder.prebuild_assemblies(self.container.phonological_memory, phonetics_path)

        for area in self.container.areas:
            area.build_structure()

    def init_zones(self):
        pr = PhoneticRecognitionZone(agent=self)
        speech_controller = SpeechControllerZone(agent=self)
        thought_controller = ThoughtControllerZone(agent=self)
        syntax_production = SyntaxProductionZone(agent=self)
        vr = VisualRecognitionZone(agent=self)
        semantic = SemanticStorageZone(agent=self)
        semantic.connect_to(vr, pr)

        self.container.add_zone(pr)
        self.container.add_zone(speech_controller)
        self.container.add_zone(thought_controller)
        self.container.add_zone(vr)
        self.container.add_zone(syntax_production)
        self.container.add_zone(semantic)

