import math
import random

from clusters.container import Container
from clusters.node import Node
from clusters.reinforce_trainer import ReinforceTrainer
from clusters.urge_resolver import UrgeResolver
from clusters.walker import Walker
from utils.file_ops import load_list_from_file
from utils.json_serializer import json_serialize
from utils.misc import split_list_in_batches


class RLNetwork:
    """
    The main entry point and the manager of all neural processes
    """
    def __init__(self, world):
        self.container = Container()
        self.world = world
        self.current_tick = 0
        self.input_nodes = []
        self.log = []
        self.episode_counter = 0
        self._create_predefined_nodes()
        self.reward_node = None


    def load_layout(self, filename):
        self.container.load(filename)


    def _create_predefined_nodes(self):
        self.reward_node = self._check_create_node('reward')


    @staticmethod
    def print_log(log):
        for log_line in log:
            print(log_line)


    def run(self, epochs=10):
        """
        Performs running cycle
        :param filename:
        :return:
        """
        return random.choice(['TurnLeft', 'TurnRight', 'Forward', 'Forward'])


    def memorize(self, action, observations, reward):
        """
        Memorizes an episode which is effectively a (action, observations, reward) tuple
        :param action:
        :return:
        """
        direct_nodes = []
        action_node = self._check_create_node(action)
        direct_nodes.append(action_node)
        observation_nodes = self._make_observation_nodes(observations)
        if not observation_nodes:
            # no observations - nothing to memorize
            return

        direct_nodes.extend(observation_nodes)

        # near signalling to awake latent nodes
        signalled_nodes = self._run_observation_set(direct_nodes)

        self.episode_counter += 1
        episode_node = self._check_create_node(f'episode {self.episode_counter}')
        episode_node.is_episode = True
        self.container.make_connection(action_node, episode_node)
        self.container.make_connection(episode_node, action_node)

        for node in signalled_nodes:
            if node not in [action_node]:
                self.container.make_connection(node, episode_node)
                self.container.make_connection(episode_node, node)

        if reward:
            self.container.make_connection(episode_node, self.reward_node)
            self.container.make_connection(self.reward_node, episode_node)


    def learn_connectome(self):
        """
        Makes and adjust connections between simultaneously firing nodes within one episode
        """
        episode_nodes = [node for node in self.container.nodes if node.is_episode]
        if len(episode_nodes) < 2:
            return
        connections_counter = {}
        for node in episode_nodes:
            self._collect_episode_callout_stats(node, connections_counter)

        pair_list = [(key, connections_counter[key]) for key in connections_counter]
        pair_list.sort(key=lambda item: item[1], reverse=True)
        top_count = pair_list[0][1]
        if top_count < 4:
            return
        # make connections for the top half of pairs
        for pair, cnt in pair_list:
            if cnt > top_count // 2:
                self._make_connection_for_pair(pair)


    def _make_connection_for_pair(self, pair_repr):
        node_ids = pair_repr.split('-')
        node1 = self.container.get_node_by_id(node_ids[0].strip())
        node2 = self.container.get_node_by_id(node_ids[1].strip())
        self.container.make_connection(node1, node2)
        self.container.make_connection(node2, node1)


    def _collect_episode_callout_stats(self, node, connections_counter):
        walker = Walker(self.container)
        fired_nodes = walker.run([node], max_ticks=2)
        local_cache = set()
        for node1 in fired_nodes:
            for node2 in fired_nodes:
                if not node1.is_episode and not node2.is_episode and node1 != node2 and node1 != node and node2 != node:
                    repr = self.get_node_pair_pattern(node1, node2)
                    if repr in local_cache:
                        continue
                    local_cache.add(repr)
                    if repr in connections_counter:
                        connections_counter[repr] += 1
                    else:
                        connections_counter[repr] = 1

    @staticmethod
    def get_node_pair_pattern(node1, node2):
        """
        Constructs a string representation of nodes pair
        """
        if int(node1.nid) > int(node2.nid):
            return f'{node2.nid} - {node1.nid}'
        else:
            return f'{node1.nid} - {node2.nid}'


    def _make_observation_nodes(self, observations):
        """
        Creates nodes for observations
        :param observations: list of observations
        :return:
        """
        observation_nodes = []
        for (obj, observation) in observations:
            object_node = self._check_create_node(obj.name)
            for key in observation:
                if observation[key]:
                    observation_node = self._check_create_node(key)
                    object_observation_id = f'{obj.name} {key}';
                    object_observation_node = self._check_create_node(object_observation_id)
                    self.container.make_connection(observation_node, object_observation_node)
                    self.container.make_connection(object_node, object_observation_node)
                    observation_nodes.append(object_observation_node)
        return observation_nodes


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


    def _run_observation_set(self, nodes):
        if len(nodes) < 2:
            return []
        walker = Walker(self.container)
        signalling_nodes = walker.run(nodes, max_ticks=2)
        signalling_nodes = [node for node in signalling_nodes if node.is_entity()]
        return signalling_nodes


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
