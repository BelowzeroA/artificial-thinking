import json

from brain.brain import Brain
from neurons.neuro_container import NeuroContainer
from utils.json_serializer import json_serialize
from utils.misc import Colors
from vision.parameters import HyperParameters
from vision.self_sustained_block import SelfSustainedActivityBlock

BATCH_SIZE = 5


class Network:

    def __init__(self, container: NeuroContainer):
        self.container = container
        self.container.network = self
        self.samples = []
        self.current_tick = 0
        self.current_epoch = 0
        self.num_epochs = 0
        self.loop_ended = False
        self._lvl3_fired = False
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


    def run(self, label=None, max_ticks=10):
        # self.container.update_connectome_cache()
        self.loop_ended = False
        result = False
        self.current_tick = 0
        self.container.current_tick = 0
        self.container.current_label = label
        while self.current_tick <= max_ticks and not self.loop_ended:
            self.current_tick += 1
            self.container.current_tick += 1
            print('Tick {}'.format(self.current_tick))
            self._update_state()
            self._update_weights()
        return result


    def _update_state(self):
        mentioned_sabs = []
        for neuron in self.container.neurons:
            neuron.update()
            self._print_state(neuron, mentioned_sabs)

        for synapse in self.container.synapses:
            synapse.update()

        if self._gaba_release and self.current_tick > self._gaba_release_start_tick + HyperParameters.gaba_release_length:
            pass
            # self._gaba_release = False

        labelled_sab = self.container.get_current_label_sab()
        if labelled_sab:
            labelled_sab.fire()

        self._print_sab_state(self.container.get_sab_by_id('001'), detailed=True)
        self._print_sab_state(self.container.get_sab_by_id('002'), detailed=True)
        self._print_sab_state(self.container.get_sab_by_id('003'), detailed=True)
        self._print_sab_state(self.container.get_sab_by_id('008'), detailed=True)
        self._print_sab_state(self.container.get_sab_by_id('010'), detailed=True)
        # self._print_sab_state(sab)


    def _print_sab_state(self, sab: SelfSustainedActivityBlock, detailed=False):
        neuron_count = 0
        caused_sabs = []
        caused_sabs_inh = []
        receptive_firings_report = []
        for neuron in sab.receptive_neurons:
            if neuron.fired:
                history_element = [hel for hel in neuron.history if hel.tick == self.current_tick][0]
                neuron_count += 1
                if history_element.external_excitation and detailed:
                    if sab.layer.layer_id == 3:
                        sabs = []
                        sabs_inhibitory = []
                        for src_neuron_id in history_element.external_excitation:
                            src_neuron = self.container.get_neuron_by_id(src_neuron_id)
                            synapse = [s for s in src_neuron.outgoing_connections if s.target == neuron][0]
                            if synapse.pulsed:
                                if synapse.inhibitory:
                                    sabs_inhibitory.append(src_neuron.clump._id)
                                else:
                                    sabs.append(src_neuron.clump._id)
                        sabs = list(set(sabs))
                        caused_sabs.extend(sabs)
                        sabs.sort()

                        sabs_inhibitory = list(set(sabs_inhibitory))
                        caused_sabs_inh.extend(sabs_inhibitory)
                        sabs_inhibitory.sort()
                        receptive_firings_report.append(
                            f'  receptive {neuron._id} excited from {sabs} inhibited from {sabs_inhibitory}')
                    else:
                        receptive_firings_report.append(
                            f'  receptive {neuron._id} from {history_element.external_excitation}')
        msg = f'SAB {sab._id} {sab.orientations} had {neuron_count} firing neurons'
        print(msg)
        caused_sabs = list(set(caused_sabs))
        caused_sabs.sort()
        caused_sabs_inh = list(set(caused_sabs_inh))
        caused_sabs_inh.sort()
        print(f'SAB {sab._id} causal exciting sabs: {caused_sabs}, inhibitory sabs: {caused_sabs_inh}')

        # for line in receptive_firings_report:
        #     print(line)


    def _print_state(self, neuron, mentioned_sabs):
        print_msg = False
        if neuron.fired and neuron.clump and neuron in neuron.clump.output_neurons:
            layer_id = neuron.clump.layer.layer_id
            if self._lvl3_fired:
                if layer_id in [2, 3]:
                    print_msg = True
            else:
                if layer_id in [3]:
                    self._layer3_sab = neuron.clump
                    print_msg = True
                    self._lvl3_fired = True
            if layer_id in [2, 3]:
                print_msg = True
        if print_msg and neuron.clump not in mentioned_sabs:
            orientations = neuron.clump.orientations
            region = neuron.clump.region
            region_coords = region.coord if region else ''
            msg = f'SAB {neuron.clump._id} {orientations} {region_coords} in layer {layer_id} fired after {self.current_tick} ticks'
            if layer_id == 3:
                msg = Colors.bold(msg)
            print(msg)
            mentioned_sabs.append(neuron.clump)


    def _update_weights(self):
        for neuron in self.container.neurons:
            neuron.update_weights()


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
