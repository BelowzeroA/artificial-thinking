import json

from lang.assembly_source import AssemblySource
from lang.data_provider import DataProvider
from neurons.neuro_container import NeuroContainer
from utils.json_serializer import json_serialize


class Network:

    def __init__(self, container: NeuroContainer, assembly_builder):
        from lang.assembly_builder import AssemblyBuilder
        self.container = container
        self.container.network = self
        self.assembly_builder: AssemblyBuilder = assembly_builder
        self.samples = []
        self.current_tick = 0
        self.num_epochs = 0
        self.loop_ended = False
        self._gaba_release = False
        self._gaba_release_start_tick = 0

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

    def load_assemblies(self):
        self.assembly_builder.prepare_assemblies(self.current_tick)

    def _update_state(self):
        for na in self.container.assemblies:
            na.update()

        for conn in self.container.connections:
            conn.update()

        self.assembly_builder.build_new_assemblies()

        self._report_fired_assemblies()

    def _update_weights(self):
        for neuron in self.container.neurons:
            neuron.update_weights()

    def _report_fired_assemblies(self):
        for na in self.container.assemblies:
            if na.fired:
                print(f'assembly {na} fired')

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
