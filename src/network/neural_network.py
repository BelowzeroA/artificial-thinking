import json

from neurons.neuro_container import NeuroContainer
from utils.json_serializer import json_serialize

LEARNING_RATE = 0.05
BATCH_SIZE = 5


class NeuralNetwork:

    def __init__(self):
        self.container = NeuroContainer()
        self.samples = []
        self.current_tick = 0
        self.current_epoch = 0
        self.num_epochs = 0
        self.batch_size = 5


    def load(self, filename):
        self.container.load(filename)
        with open(filename, 'r', encoding='utf-8') as data_file:
            content = json.load(data_file)
        self.samples = content['samples']


    def fit(self, num_epochs=10, verbose=True):
        self.num_epochs = num_epochs
        number_of_batches = int(num_epochs / BATCH_SIZE)
        batch_thresholds =[]
        thresholds_are_set = False
        for batch in range(number_of_batches):
            if thresholds_are_set:
                thresholds = self.container.assign_random_thresholds()
            results = []
            for _ in range(BATCH_SIZE):
                self.current_epoch += 1
                for sample in self.samples:
                    self.fire_input(sample)
                    if not thresholds_are_set:
                        thresholds = self.container.assign_random_thresholds()
                        thresholds_are_set = True
                    result = self._fit_on_sample(sample, verbose)
                    results.append(int(result))
            batch_thresholds.append((thresholds, sum(results)))
        batch_thresholds.sort(key=lambda x: x[1], reverse=True)
        thresholds = batch_thresholds[0][0]
        self.container.set_thresholds(thresholds)


    def _fit_on_sample(self, sample, verbose):
        self._reset_histories()
        return self._run(sample, verbose=verbose)


    def _run(self, sample, max_ticks=10, verbose=True):
        loop_ended = False
        result = False
        self.current_tick = 0
        while self.current_tick <= max_ticks and not loop_ended:
            self.current_tick += 1
            self._update_step()
            loop_ended, result = self._check_result(sample)
        if verbose:
            # print(self.get_state())
            print('epoch {}/{}: {}'.format(self.current_epoch, self.num_epochs, result))
        if result:
            self._update_on_reward()
        else:
            self._update_on_punishment()
        return result


    def _update_on_reward(self):
        for synapse in self.container.synapses:
            synapse.update_weight(LEARNING_RATE)
        for neuron in self.container.neurons:
            neuron.update_threshold()


    def _update_on_punishment(self):
        for synapse in self.container.synapses:
            synapse.update_weight(-LEARNING_RATE)
        # for neuron in self.container.neurons:
        #     neuron.update_threshold()


    def _reset_histories(self):
        for synapse in self.container.synapses:
            synapse.reset_history()
        for neuron in self.container.neurons:
            neuron.reset_history()


    def _check_result(self, sample):
        output = sample['output']
        negative = False
        if output.startswith('~'):
            negative = True
            output = output[1:]
        neuron = self.container.get_neuron_by_id(output)
        if negative:
            if neuron.fired:
                return True, False
            else:
                return False, True
        else:
            if neuron.fired:
                return True, True
            else:
                return False, False


    def _update_step(self):
        for neuron in self.container.neurons:
            neuron.update()
        for synapse in self.container.synapses:
            synapse.update()


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
