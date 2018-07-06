import json

from clusters.connection import Connection
from clusters.node import Node


class Container:

    def __init__(self):
        self.nodes = []
        self.connections = []
        self.reinforcement_mode = False
        self.consolidation_mode = False


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

        for entry in self.entries['nodes']:
            node = Node(id=entry['id'], pattern=entry['patterns'][0], container=self)
            if 'abstract' in entry:
                node.abstract = entry['abstract']
            self.nodes.append(node)

        for entry in self.entries['connections']:
            source_node = self.get_node_by_id(entry['source'])
            target_node = self.get_node_by_id(entry['target'])
            connection = Connection(source=source_node, target=target_node, container=self)
            connection.weight = entry['weight']
            self.connections.append(connection)