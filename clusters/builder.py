from clusters.container import Container
from clusters.node import Node
from utils.json_serializer import json_serialize


class Builder:

    def __init__(self):
        self.nodes = []
        self.stop_words = ['a', 'is', 'in']
        self.container = Container()


    @staticmethod
    def load_list_from_file(filename):
        lines = []
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                lines.append(line.strip())
        return lines


    def build_net(self, filename):
        lines = Builder.load_list_from_file(filename)
        for line in lines:
            tokens = line.split()
            self._build_from_tokens(tokens)


    def _build_from_tokens(self, tokens):
        delimiter = 0
        if 'is' in tokens:
            delimiter = tokens.index('is')
        for i, token in enumerate(tokens):
            if i == delimiter and delimiter > 0:
                continue
            self._check_make_node(token)
        if len(tokens) < 2:
            return
        if delimiter > 0:
            whole_pattern = ' '.join(tokens)
            tokens_before = tokens[:delimiter]
            tokens_after = tokens[delimiter + 1:]
            node_before = self._build_abstract_node(tokens_before)
            node_after = self._build_abstract_node(tokens_after)
            node_connector = Node(self.container.next_node_id(), whole_pattern, container=self.container, abstract=True)
            self.container.make_connection(node_before, node_connector)
            self.container.make_connection(node_connector, node_after)
        else:
            self._build_abstract_node(tokens)


    def _build_abstract_node(self, tokens):
        if len(tokens) == 1:
            return self.container.get_node_by_pattern(tokens[0])
        pattern = ' '.join(tokens)
        seq_node = Node(self.container.next_node_id(), pattern, container=self.container, is_sequence=True, abstract=True)
        for token in tokens:
            node = self.container.get_node_by_pattern(token)
            self.container.make_connection(node, seq_node)
        return seq_node


    def _check_make_node(self, token):
        node = self.container.get_node_by_pattern(token)
        if not node:
            node = Node(self.container.next_node_id(), pattern=token, container=self.container, abstract=False)
            self.container.append_node(node)
            synth_node = Node(self.container.next_node_id(), pattern='synth: ' + token,
                              container=self.container, abstract=False)
            self.container.append_node(synth_node)
            self.container.make_connection(node, synth_node)
        return node


    def store(self, filename):
        out_val = {'nodes': self.container.nodes,
                   'connections': self.container.connections}
        with open(filename, mode='wt', encoding='utf-8') as output_file:
            print(json_serialize(out_val), file=output_file)

