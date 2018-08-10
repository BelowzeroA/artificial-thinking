import json

from clusters.circuit import Circuit
from clusters.connection import Connection
from clusters.node import Node


class Container:

    def __init__(self):
        self.nodes = []
        self.connections = []
        self.reinforcement_mode = False
        self.consolidation_mode = False
        self.urge_mode = False
        self._create_synth_node()


    def _create_synth_node(self):
        self.synth_node = Node(self.next_node_id(), 'synth abstract', container=self, abstract=True)
        self.append_node(self.synth_node)


    def get_node_by_pattern(self, pattern):
        nodes = [cl for cl in self.nodes if cl.pattern == pattern]
        if nodes:
            return nodes[0]
        return None


    def get_node_by_id(self, id):
        nodes = [cl for cl in self.nodes if cl.nid == id]
        if nodes:
            return nodes[0]
        return None


    def next_node_id(self):
        if len(self.nodes) == 0:
            return '1'
        return str(max([int(cl.nid) for cl in self.nodes]) + 1)


    def append_node(self, node):
        self.nodes.append(node)


    def append_connection(self, conn):
        self.connections.append(conn)


    def get_outgoing_connections(self, node):
        return [conn for conn in self.connections if conn.source == node]


    def get_incoming_connections(self, node):
        return [conn for conn in self.connections if conn.target == node]


    def make_connection(self, source, target):
        conn = self.get_connection(source=source, target=target)
        if conn:
            return conn
        conn = Connection(container=self, source=source, target=target)
        source.output.append(conn)
        self.connections.append(conn)
        return conn


    def get_connection(self, source, target):
        conns = [conn for conn in self.connections if conn.source == source and conn.target == target]
        if conns:
            return conns[0]
        return None


    def are_nodes_connected(self, node1, node2):
        c1 = [conn for conn in self.connections if conn.source == node1 and conn.target == node2]
        c2 = [conn for conn in self.connections if conn.source == node2 and conn.target == node1]
        return len(c1) > 0 or len(c2) > 0


    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as data_file:
            entries = json.load(data_file)

        for entry in entries['nodes']:
            node = self.get_node_by_pattern(entry['pattern'])
            if not node:
                node = Node(nid=entry['id'], pattern=entry['pattern'], container=self)
                node.abstract = self._read_property(entry, 'abstract', False)
                node.is_episode = self._read_property(entry, 'episode', False)
                self.nodes.append(node)

        # for entry in [entry for entry in entries['nodes'] if 'remembered_patterns' in entry]:
        #     node = self.get_node_by_id(entry['id'])
        #     for pattern in entry['remembered_patterns']:
        #         self._append_firing_pathway(node, pattern)

        for entry in entries['connections']:
            source_node = self.get_node_by_id(entry['source'])
            target_node = self.get_node_by_id(entry['target'])
            self.make_connection(source=source_node, target=target_node)

        if 'circuits' in entries:
            for entry in entries['circuits']:
                node = self.get_node_by_id(entry['node'])
                circuit = Circuit.load_from_json(node, self, entry)
                node.append_circuit(circuit)


    def get_circuits_to_store(self):
        circuits = []
        for node in self.nodes:
            for circuit in node.circuits:
                if circuit.fixed_firing_energy > 0:
                    circuits.append(circuit)
        return circuits


    def get_all_circuits(self):
        return [c for c in [node.circuits for node in self.nodes]]


    def _append_firing_pathway(self, node, pattern):
        inputs = []
        output = self.get_node_by_id(pattern[2])
        ids = pattern[1].split(',')
        for id in ids:
            inputs.append(self.get_node_by_id(id.strip()))
        node.firing_pathways.append({'inputs': inputs, 'output': output})


    @staticmethod
    def _read_property(entry, prop_name, default_value=''):
        if prop_name in entry:
            return entry[prop_name]
        else:
            return default_value