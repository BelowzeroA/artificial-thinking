import json

from brain.brain import Brain
from neurons.synapse import Synapse
from neurons.neuron import Neuron


class NeuroContainer:

    def __init__(self):
        self.entries = {}
        self.neurons = []
        self.clumps = []
        self.synapses = []
        self.brain = None


    def append_neuron(self, neuron):
        self.neurons.append(neuron)


    def append_clump(self, clump):
        self.clumps.append(clump)


    def append_synapses(self, synapses):
        self.synapses.extend(synapses)


    def reset(self):
        for node in self.nodes:
            node.reset()
        for connection in self.connections:
            connection.reset()


    def next_neuron_id(self):
        if len(self.neurons) == 0:
            return '1'
        return str(max([int(neuron._id) for neuron in self.neurons]) + 1)


    def next_clump_id(self):
        if len(self.clumps) == 0:
            return '1'
        return str(max([int(clump._id) for clump in self.clumps]) + 1)


    def get_neuron_by_id(self, id):
        nodes = [node for node in self.neurons if node._id == id]
        if nodes:
            return nodes[0]
        return None


    def assign_random_thresholds(self):
        thresholds_dict = {}
        for neuron in self.neurons:
            if not neuron.initial:
                neuron.assign_random_threshold()
                thresholds_dict[neuron] = neuron.threshold
        return thresholds_dict


    def set_thresholds(self, thresholds):
        for neuron in thresholds:
            neuron.threshold = thresholds[neuron]


    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as data_file:
            content = json.load(data_file)
        layout = content['layout']

        for entry in layout['neurons']:
            neuron = Neuron(id=entry['id'], container=self)
            neuron.pattern = entry['pattern']
            self.neurons.append(neuron)

        for entry in layout['synapses']:
            synapse = Synapse(
                source=self.get_neuron_by_id(entry['source']),
                target=self.get_neuron_by_id(entry['target']),
                inhibitory=entry['inhibitory'])
            synapse.weight = entry['weight']
            self.synapses.append(synapse)


    def get_clump_by_pattern(self, pattern):
        clumps = [clump for clump in self.clumps if clump.pattern == pattern]
        if clumps:
            return clumps[0]
        return None


    def get_outgoing_connections(self, neuron):
        return [conn for conn in self.synapses if conn.source == neuron]


    def get_incoming_connections(self, node):
        return [conn for conn in self.connections if conn.target == node]


    def get_connection_between_nodes(self, source, target):
        connections = [conn for conn in self.connections if conn.target == target and conn.source == source]
        if connections:
            return connections[0]
        return None


    def are_nodes_connected(self, node1, node2, primary_only=False):
        c1 = [conn for conn in self.connections if conn.source == node1 and conn.target == node2 and
                    (not conn.secondary or primary_only == False)]
        c2 = [conn for conn in self.connections if conn.source == node2 and conn.target == node1 and
                    (not conn.secondary or primary_only == False)]
        return len(c1) > 0 or len(c2) > 0



    def __repr__(self):
        repr = ''
        for node in self.nodes:
            firing_symbol = 'F' if node.firing else ' '
            if node.potential > 0:
                repr += '[{} p:{:4.1f}] '.format(node.node_id, node.potential)
        return repr

