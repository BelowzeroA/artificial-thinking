import json

from clusters.container import Container
from clusters.node import Node
from clusters.walker import Walker
from utils.file_ops import load_list_from_file
from utils.json_serializer import json_serialize
from utils.misc import split_list_in_batches


class Network:

    def __init__(self):
        self.container = Container()
        self.current_tick = 0
        self.input_nodes = []


    def load_layout(self, filename):
        self.container.load(filename)


    def run_interactions(self, filename):
        lines = load_list_from_file(filename)
        batches = split_list_in_batches(lines)
        for batch in batches:
            self._run_interaction_batch(batch)


    def _run_interaction_batch(self, batch):
        signalling_nodes = []
        for line in batch:
            nodes = self._run_interaction_line(line)
            signalling_nodes.extend(nodes)
        if len(batch) > 1:
            self._create_batch_node(list(set(signalling_nodes)))


    def _create_batch_node(self, nodes):
        combining_node = self._create_combining_node(nodes, abstract=True)


    def _run_interaction_line(self, line):
        nodes = self._create_nodes(line)
        walker = Walker(self.container)
        signalling_nodes = walker.run(nodes)
        there_is_abstract = len([1 for node in signalling_nodes if node.abstract]) > 0
        if there_is_abstract:
            signalling_nodes = [node for node in signalling_nodes if node.abstract]
        return signalling_nodes


    def _create_nodes(self, line):
        simultaneous_mode = line[0] == '['
        line = self._strip_key_chars(line)
        entities = line.split()
        nodes = []
        audial_nodes = []
        for entity in entities:
            if not self._is_visual(entity):
                entity = 'a:' + entity
            node = self._check_create_node(entity)
            nodes.append(node)
            if not self._is_visual(entity):
                audial_nodes.append(node)

        combining_node = self._create_combining_node(nodes)
        if simultaneous_mode:
            self._create_synth_node(combining_node)

        return nodes


    def _create_combining_node(self, nodes, abstract=False):
        if len(nodes) < 2:
            return None
        pattern = ' '.join([self._clear_prefix(node.pattern) for node in nodes if not self._is_visual(node.pattern)])
        there_is_visual = len([1 for node in nodes if self._is_visual(node.pattern)]) > 0
        node = Node(self.container.next_node_id(), pattern, self.container, abstract=abstract or not there_is_visual)
        self.container.append_node(node)
        for input_node in nodes:
            self.container.make_connection(input_node, node)
        return node


    def _create_synth_node(self, node):
        pattern = 'synth: ' + node.pattern
        synth_node = Node(self.container.next_node_id(), pattern, self.container)
        self.container.make_connection(node, synth_node)
        self.container.append_node(synth_node)


    def _check_create_node(self, entity):
        node = self.container.get_node_by_pattern(entity)
        if not node:
            node = Node(self.container.next_node_id(), pattern=entity, container=self.container)
            self.container.append_node(node)
        return node


    def save_layout(self, filename):
        out_val = {'nodes': self.container.nodes,
                   'connections': self.container.connections}
        with open(filename, mode='wt', encoding='utf-8') as output_file:
            print(json_serialize(out_val), file=output_file)


    @staticmethod
    def _strip_key_chars(line):
        return line.strip('[]?')

    @staticmethod
    def _is_visual(line):
        return line.startswith('v:')\

    @staticmethod
    def _clear_prefix(line):
        if line[1:2] == ':':
            return line[2:]
        return line
