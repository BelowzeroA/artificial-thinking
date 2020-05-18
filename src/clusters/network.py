import math

from clusters.container import Container
from clusters.hyper_parameters import FINGERPRINT_LENGTH
from clusters.memory_consolidator import MemoryConsolidator
from clusters.node import Node
from clusters.reinforce_trainer import ReinforceTrainer
from clusters.urge_resolver import UrgeResolver
from clusters.walker import Walker
from utils.file_ops import load_list_from_file
from utils.json_serializer import json_serialize
from utils.misc import split_list_in_batches


class Network:
    """
    The main entry point and the manager of all neural processes
    """
    def __init__(self):
        self.container = Container()
        self.current_tick = 0
        self.input_nodes = []
        self.tests = []
        self.log = []


    def load_layout(self, filename):
        self.container.load(filename)


    @staticmethod
    def print_log(log):
        for log_line in log:
            print(log_line)


    def run_interactions(self, filename):
        """
        Performs interactions on batches from file
        :param filename:
        :return:
        """
        lines = load_list_from_file(filename)
        # self._load_tests(lines)
        batches = split_list_in_batches(lines)
        result = {}
        for batch in batches:
            batch_results = self._run_interaction_batch(batch)
            batch_repr = ', '.join(batch)
            result[batch_repr] = (batch_results, list(self.log))
            self.log.clear()
        return result


    def _run_interaction_batch(self, batch):
        """
        Parses and runs an interaction batch
        Interaction batch is a group of sensor inputs coming together in a short timeframe
        Batch sample:
            v:mom
            [v:bunny bunny]
        Means that "Mom" is near the "baby" showing her a toy "bunny" and saying a word "bunny"
        :param batch:
        :return:
        """
        if len(batch) == 1:
            return self._run_one_line_batch(batch[0])
        else:
            return self._run_multiline_batch(batch)


    def _run_one_line_batch(self, batch):
        """
        :param batch:
        :return:
        """
        result_nodes = []
        signalling_nodes = []

        entities = batch.split()
        for entity in entities:
            node = self._create_triple(entity)
            signalling_nodes.append(node)

        self._create_batch_node(signalling_nodes)
        # nodes, second_order_signaled_nodes = self._run_interaction_line(batch)
        #
        # signalling_nodes.extend(second_order_signaled_nodes)
        #
        # self._create_batch_node(list(set(signalling_nodes)))

        return result_nodes


    def _run_multiline_batch(self, batch):
        """
        Parses and runs an interaction batch
        Interaction batch is a group of sensor inputs coming together in a short timeframe
        Batch sample:
            v:mom
            [v:bunny bunny]
        Means that "Mom" is near the "baby" showing her a toy "bunny" and saying a word "bunny"
        :param batch:
        :return:
        """
        result_nodes = []
        signalling_nodes = []
        is_urge = len([line for line in batch if line.endswith('?')]) > 0
        is_reinforcement = not is_urge and len([line for line in batch if '?' in line]) > 0
        first_order_nodes = []
        for line in batch:
            if line.endswith('?'):
                result = self._run_urge_line(line, first_order_nodes)
                result_nodes.extend(result)
            elif '?' in line:
                self._run_reinforcement_line(line, signalling_nodes)
            else:
                if is_reinforcement:
                    nodes = self._create_nodes(line)
                    signalling_nodes.extend(nodes)
                else:
                    nodes, second_order_signaled_nodes = self._run_interaction_line(line)
                    signalling_nodes.extend(second_order_signaled_nodes)
                    first_order_nodes.extend(nodes)

        if len(batch) > 1 and not is_reinforcement:
            self._create_batch_node(list(set(signalling_nodes)))

        return result_nodes


    def _run_urge_line(self, line, signalling_nodes):
        nodes = self._create_nodes(line)
        signalling_nodes.extend(nodes)
        resolver = UrgeResolver(self.container, self.log)
        result = resolver.run(signalling_nodes)
        return result


    def _create_batch_node(self, nodes):
        nodes = [node for node in nodes if node.is_entity()]
        if not self._nodes_are_all_connected(nodes):
            self._create_combining_node(nodes, abstract=True, episode=True)


    def _nodes_are_all_connected(self, nodes):
        for spotted in nodes:
            connection_exists = False
            for counterpart in nodes:
                if spotted == counterpart:
                    continue
                if self.container.are_nodes_connected(spotted, counterpart):
                    connection_exists = True
                    break
            if not connection_exists:
                return False
        return True


    def _run_interaction_line(self, line):
        nodes = self._create_nodes(line)
        walker = Walker(self.container)
        signalling_nodes = walker.run(nodes, max_ticks=2)
        signalling_nodes = [node for node in signalling_nodes if node.is_entity()]
        return nodes, signalling_nodes


    def _run_reinforcement_line(self, line, signalling_nodes):
        q_pos = line.find('?')
        nodes = self._create_nodes(line[:q_pos])
        target_nodes = self._create_nodes(line[q_pos + 1:])
        signalling_nodes.extend(nodes)
        trainer = ReinforceTrainer(self.container)
        signalling_nodes = trainer.run(signalling_nodes, target_nodes)
        return signalling_nodes


    def _create_nodes(self, line):
        simultaneous_mode = line[0] == '['
        line = self._strip_key_chars(line)
        entities = line.split()
        nodes = []
        audial_nodes = []
        for entity in entities:
            audial = not self._is_visual(entity) and not self._is_synthesizer(entity)
            if audial:
                entity = 'a:' + entity
            node = self._check_create_node(entity)
            nodes.append(node)
            if audial:
                audial_nodes.append(node)

        combining_node = self._create_combining_node(nodes)
        if simultaneous_mode:
            self._create_synth_node(combining_node)
        # case of a single visual input
        if not combining_node and len(nodes) == 1 and nodes[0].is_visual():
            self._create_single_projection_node(nodes[0])
        return nodes


    def _create_triple(self, entity):
        center_node = self._check_create_node(entity)
        audio_node = self._check_create_node('a:' + entity)
        synth_node = self._check_create_node('synth:' + entity)
        self.container.make_connection(audio_node, center_node)
        self.container.make_connection(center_node, synth_node)
        self.container.make_connection(synth_node, self.container.synth_node)
        self.container.make_connection(self.container.synth_node, synth_node)
        return center_node


    def _create_combining_node(self, nodes, abstract=False, episode=False):
        if len(nodes) < 2:
            return None
        pattern = ' '.join([self._clear_prefix(node.pattern) for node in nodes if not self._is_visual(node.pattern)])
        node = self.container.get_node_by_pattern(pattern)
        if node:
            return node
        there_is_visual = len([1 for node in nodes if self._is_visual(node.pattern)]) > 0
        node = Node(self.container.next_node_id(), pattern, self.container, abstract=abstract or not there_is_visual)
        node.is_episode = episode
        self.container.append_node(node)
        for input_node in nodes:
            self.container.make_connection(input_node, node)
            if not input_node.is_visual() and not input_node.is_auditory():
                self.container.make_connection(node, input_node)
            synth_node = self.container.get_node_by_pattern('synth:' + input_node.pattern)
            if synth_node:
                self.container.make_connection(node, synth_node)
        return node


    def sleep(self):
        for _ in range(8):
            self._sleep_phase()


    def _sleep_phase(self):
        consolidator = MemoryConsolidator(self.container)
        node_weights = {}
        conn_weights = {}
        pulses = 20
        for _ in range(pulses):
            node_counters, conn_counters = consolidator.run()
            for node in node_counters:
                if node in node_weights:
                    node_weights[node] += node_counters[node]
                else:
                    node_weights[node] = node_counters[node]

            for conn in conn_counters:
                if conn in conn_weights:
                    conn_weights[conn] += conn_counters[conn]
                else:
                    conn_weights[conn] = conn_counters[conn]

        node_weights = {node: node_weights[node] for node in node_weights
                        if not node.is_special() and not node.is_episode }
        max_weight_node = max(node_weights, key=node_weights.get)
        max_weight = node_weights[max_weight_node]
        mean = max_weight / 2
        self._upgrade_nodes_mass(node_weights, mean)

        hub_nodes = [node for node in node_weights if not node.is_twin() and node_weights[node] > max_weight * 0.8]
        for node in hub_nodes:
            self._create_twin_node(node)


    @staticmethod
    def _upgrade_nodes_mass(node_weights, mean):
        for node in node_weights:
            node.mass *= math.sqrt(node_weights[node] / mean)


    def _create_twin_node(self, source_node):
        pattern = source_node.pattern + ' twin'
        node = self.container.get_node_by_pattern(pattern)
        if node:
            return node
        node = Node(self.container.next_node_id(), pattern, self.container, abstract=True)
        self.container.append_node(node)
        adjacent_nodes = [conn.target for conn in self.container.get_outgoing_connections(source_node)
                          if conn.target.is_entity()]
        for adjacent_node in adjacent_nodes:
            self.container.make_connection(adjacent_node, node)
            self.container.make_connection(node, adjacent_node)
            adjacent_2nd_nodes = [conn.target for conn in self.container.get_outgoing_connections(adjacent_node)
                                  if conn.target not in [source_node, node] and conn.target.is_entity()]
            for adjacent_2nd_node in adjacent_2nd_nodes:
                self.container.make_connection(adjacent_2nd_node, node)
                self.container.make_connection(node, adjacent_2nd_node)

        self.container.make_connection(source_node, node)

        return node


    def _create_single_projection_node(self, source_node):
        pattern = self._clear_prefix(source_node.pattern)
        node = self.container.get_node_by_pattern(pattern)
        if node:
            return node
        node = Node(self.container.next_node_id(), pattern, self.container, abstract=False)
        self.container.append_node(node)
        self.container.make_connection(source_node, node)
        return node


    def _create_synth_node(self, node):
        pattern = 'synth:' + node.pattern
        synth_node = Node(self.container.next_node_id(), pattern, self.container)
        self.container.make_connection(node, synth_node)
        self.container.append_node(synth_node)
        self.container.make_connection(synth_node, self.container.synth_node)
        self.container.make_connection(self.container.synth_node, synth_node)


    def _check_create_node(self, entity):
        node = self.container.get_node_by_pattern(entity)
        if not node:
            node = Node(self.container.next_node_id(), pattern=entity, container=self.container)
            self.container.append_node(node)
        return node


    def save_layout(self, filename):
        out_val = {'nodes': self.container.nodes,
                   'circuits': self.container.get_circuits_to_store(),
                   'connections': self.container.connections}
        with open(filename, mode='wt', encoding='utf-8') as output_file:
            print(json_serialize(out_val), file=output_file)


    @staticmethod
    def _strip_key_chars(line):
        return line.strip('[]?')


    @staticmethod
    def _is_auditory(line):
        return line.startswith('a:')


    @staticmethod
    def _is_visual(line):
        return line.startswith('v:')


    @staticmethod
    def _is_synthesizer(line):
        return line.startswith('synth:')


    @staticmethod
    def _clear_prefix(line):
        if line[1:2] == ':':
            return line[2:]
        return line
