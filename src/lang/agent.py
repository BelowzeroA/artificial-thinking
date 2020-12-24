import importlib

from typing import List

from lang.neural_gate import NeuralGate
from lang.primitives.inter_area_message import InterAreaMessage
from lang.zones.named_visual_objects_zone import NamedVisualObjectsZone
from lang.zones.phonetic_recognition_zone import PhoneticRecognitionZone
from lang.zones.phrase_encoder_zone import PhraseEncoderZone
from lang.zones.phrase_integrator_zone import PhraseIntegratorZone
from lang.zones.speech_controller_zone import SpeechControllerZone
from lang.zones.speech_production_zone import SpeechProductionZone
from lang.zones.syntax_production_zone import SyntaxProductionZone
from lang.zones.thought_controller_zone import ThoughtControllerZone
from lang.zones.visual_lexicon_zone import VisualLexiconZone
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

        # self.container.network = self
        dp = DataProvider(environment.filename)
        environment.scenario_length = dp.scenario_length
        self.assembly_builder = AssemblyBuilder(agent=self, data_provider=dp)
        self.samples = []
        self.environment = environment
        self.loop_ended = False
        self._messages = []
        self.init_zones()
        self.doped_ticks = []
        self.stressed_ticks = []

    def reset(self):
        self.container.current_tick = 0

    def queue_message(self, msg_name: str, data: dict = None):
        msg = InterAreaMessage(msg_name)
        msg.data = data
        self._messages.append(msg)

    def update(self):
        self.queue_message('on_tick_beginning')
        self.load_assemblies()
        self._update_state()
        # self._update_weights()

    def build_predefined_assemblies(self):
        for zone in self.container.zones:
            zone.build_predefined_assemblies()

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

    def load_assemblies(self):
        current_tick = self.environment.current_tick
        assembly_source = self.assembly_builder.get_assembly_source(current_tick)
        if assembly_source:
            if self.environment.verbosity > 0:
                print()
                print(f'Scenario line: {assembly_source.source_line}')
            for zone in self.container.zones:
                zone.prepare_assemblies(assembly_source, current_tick)

    def _update_state(self):
        self._handle_message_queue()

        for zone in self.container.zones:
            zone.before_assemblies_update(self.environment.current_tick)

        self._handle_message_queue()

        for na in self.container.assemblies:
            na.update(self.environment.current_tick)

        for conn in self.container.connections:
            conn.update()

        self._handle_message_queue()

        self.assembly_builder.build_new_assemblies()

        self.absorb_neurotransmitters()

        if self.environment.verbosity > 0:
            self._report_fired_assemblies()

    def _report_fired_assemblies(self):
        for na in self.container.assemblies:
            if na.fired:
                self.environment.report_on_area(na.area, f'area {na.area} assembly {na} fired')

        for area in self.container.areas:
            if self.environment.current_tick in area.inhibited_at_ticks:
                self.environment.report_on_area(area, f'area {area} is inhibited')

    def utter(self, utterance: str):
        self.environment.receive_utterance(self, utterance)

    def receive_dope(self):
        self.doped_ticks.append(self.environment.current_tick + 1)

    def absorb_neurotransmitters(self):
        # Dopamine-induced excitation
        if self.environment.current_tick in self.doped_ticks:
            for zone in self.container.zones:
                zone.receive_dope()

        # Stress-induced inhibition
        if self.environment.current_tick in self.stressed_ticks:
            for zone in self.container.zones:
                zone.receive_cortisol()

    def current_assembly_source(self):
        current_tick = self.environment.current_tick
        assembly_source = None
        for tick in self.assembly_builder.data_provider:
            if tick > current_tick:
                return assembly_source
            assembly_source = self.assembly_builder.data_provider[tick]
        return assembly_source

    def save_model(self, filename):
        out_val = {'neurons': self.container.neurons,
                   'synapses': self.container.synapses}
        with open(filename, mode='wt', encoding='utf-8') as output_file:
            print(json_serialize(out_val), file=output_file)

    def get_state(self):
        repr = ' '.join([str(neuron) for neuron in self.container.neurons])
        return '{}: {}'.format(str(self.current_tick), repr)

    def init_zones(self):
        # zones
        pr = PhoneticRecognitionZone(agent=self)

        thought_controller = ThoughtControllerZone(agent=self)
        # syntax_production = SyntaxProductionZone(agent=self)
        vr = VisualRecognitionZone(agent=self)
        vl = VisualLexiconZone(agent=self)

        nvo = NamedVisualObjectsZone(agent=self)
        nvo.connect_to(vr, pr)

        vl.connect_to([nvo, vr])

        phrase_integrator = PhraseIntegratorZone(agent=self)
        phrase_integrator.connect_to(pr, nvo)

        phrase_enc = PhraseEncoderZone(agent=self)
        phrase_enc.connect_to(phrase_integrator)
        # syntax_production.connect_to([vl])

        speech_production = SpeechProductionZone(agent=self)
        # speech_production.connect_to([syntax_production])
        speech_production.connect_to([vl])

        self.container.add_zone(vr)
        self.container.add_zone(pr)
        self.container.add_zone(vl)
        self.container.add_zone(phrase_enc)
        self.container.add_zone(phrase_integrator)
        self.container.add_zone(thought_controller)
        # self.container.add_zone(syntax_production)
        self.container.add_zone(nvo)
        self.container.add_zone(speech_production)

        # Gates
        vl_syntax_gate = NeuralGate(agent=self, source=vl.output_area, target=speech_production.input_area)
        self.container.add_gate(vl_syntax_gate)

        # br_speech_gate = NeuralGate(
        #     agent=self,
        #     source=syntax_production.output_areas()[0],
        #     target=speech_production.input_area
        # )
        # self.container.add_gate(br_speech_gate)

        # controller zones
        speech_controller = SpeechControllerZone(agent=self)

        speech_controller.connect_to_sensors([vl.output_tone_area] + phrase_enc.output_areas())
        speech_controller.connect_to_gate(vl_syntax_gate)
        # speech_controller.connect_to_gate(br_speech_gate)
        self.container.add_zone(speech_controller)

