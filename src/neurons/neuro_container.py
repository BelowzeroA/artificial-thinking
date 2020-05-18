import json
from typing import List, Iterable

from lang.connection import Connection
from lang.neural_area import NeuralArea
from lang.neural_zone import NeuralZone
from neurons.synapse import Synapse
from neurons.neuron import Neuron
from vision.parameters import SabParameters


class NeuroContainer:

    def __init__(self, agent: 'Agent'):
        from vision.self_sustained_block import SelfSustainedActivityBlock
        from lang.neural_area import NeuralArea
        self.entries = {}
        self.agent = agent
        self.neurons: List[Neuron] = []
        self.assemblies = []
        self.zones: List[NeuralZone]  = []
        self.sabs: List[SelfSustainedActivityBlock] = []
        self.synapses: List[Synapse] = []
        self.connections: List[Connection] = []
        self.brain = None
        self.current_tick: int = 0
        self.current_label = None
        self.network = None
        self.areas: List[NeuralArea] = []
        self.default_area = None
        self.phonological_memory: 'PhonologicalMemory' = None
        self.vocal_area: 'VocalArea' = None

    def append_neuron(self, neuron):
        self.neurons.append(neuron)

    def add_areas(self, areas: List):
        self.areas.extend(areas)

    def add_area(self, area: 'NeuralArea'):
        self.areas.append(area)

    def add_zone(self, zone: NeuralZone):
        self.zones.append(zone)

    def create_neuron(self):
        neuron = Neuron(id=self.next_neuron_id(), container=self)
        self.neurons.append(neuron)
        return neuron

    def create_assembly(self, pattern: str):
        from lang.neural_assembly import NeuralAssembly
        na = NeuralAssembly(id=self.next_assembly_id(), container=self)
        na.pattern = pattern
        self.assemblies.append(na)
        return na

    def get_area_by_prefix(self, prefix: str) -> 'NeuralArea':
        if prefix is None:
            return self.default_area
        for area in self.areas:
            if area.corresponds_to_prefix(prefix):
                return area
        return None

    def create_sab(self, layer, params: SabParameters):
        from vision.self_sustained_block import SelfSustainedActivityBlock
        sab = SelfSustainedActivityBlock(id=self.next_sab_id(), container=self, layer=layer, params=params)
        self.sabs.append(sab)
        return sab

    def get_current_label_sab(self):
        if not self.current_label:
            return None
        found = [sab for sab in self.sabs if sab.label == self.current_label]
        if found:
            return found[0]
        else:
            return None

    from lang.neural_assembly import NeuralAssembly
    def create_connection(self, source: NeuralAssembly, target: NeuralAssembly) -> Connection:
        con = Connection(container=self, source=source, target=target)
        self.connections.append(con)
        return con

    def create_synapse(self, source: Neuron, target: Neuron) -> Synapse:
        synapse = Synapse(source=source, target=target)
        synapse.inhibitory = source.inhibitory
        self.synapses.append(synapse)
        return synapse

    def append_clump(self, clump):
        self.clumps.append(clump)

    def append_synapses(self, synapses):
        self.synapses.extend(synapses)

    def reset(self):
        for node in self.nodes:
            node.reset()
        for connection in self.connections:
            connection.reset()

    def update_connectome_cache(self):
        for neuron in self.neurons:
            neuron.update_connectome_cache()

    def next_neuron_id(self):
        if len(self.neurons) == 0:
            return '1'
        return str(max([int(neuron._id) for neuron in self.neurons]) + 1)

    def next_assembly_id(self):
        if len(self.assemblies) == 0:
            return '1'
        return str(max([int(a.id) for a in self.assemblies]) + 1)

    def next_sab_id(self):
        if len(self.sabs) == 0:
            return '001'
        int_number = max([int(sab._id) for sab in self.sabs]) + 1
        return f'{int_number:03d}'


    def next_clump_id(self):
        if len(self.clumps) == 0:
            return '1'
        return str(max([int(clump._id) for clump in self.clumps]) + 1)


    def get_sab_by_id(self, id: str):
        sabs = [sab for sab in self.sabs if sab._id == id]
        if sabs:
            return sabs[0]
        return None

    def get_neural_area_assemblies(self, area: NeuralArea) -> Iterable[NeuralAssembly]:
        return [na for na in self.assemblies if na.area == area]

    def get_assembly_by_pattern(self, pattern):
        assemblies = [na for na in self.assemblies if na.pattern == pattern]
        if assemblies:
            return assemblies[0]
        return None

    def get_assembly_by_id(self, id: str):
        assemblies = [na for na in self.assemblies if na.id == id]
        if assemblies:
            return assemblies[0]
        return None

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


    def get_neuron_outgoing_connections(self, neuron):
        return [conn for conn in self.synapses if conn.source == neuron]

    def get_assembly_outgoing_connections(self, na: NeuralAssembly) -> List[Connection]:
        return [conn for conn in self.connections if conn.source == na]

    def get_incoming_connections(self, node):
        return [conn for conn in self.synapses if conn.target == node]

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



    # def __repr__(self):
    #     repr = ''
    #     for node in self.nodes:
    #         firing_symbol = 'F' if node.firing else ' '
    #         if node.potential > 0:
    #             repr += '[{} p:{:4.1f}] '.format(node.node_id, node.potential)
    #     return repr

