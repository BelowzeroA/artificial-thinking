import itertools
import operator

import math

from clusters.network_runner import NetworkRunner


class ReinforceTrainer(NetworkRunner):

    def __init__(self, container):
        super().__init__(container=container)
        self.container.reinforcement_mode = True
        self.fired_nodes = []
        self.target_nodes = []
        self.target_achieved = False


    def run(self, initial_nodes, target_nodes, num_trains=5):
        self.initial_nodes = initial_nodes
        self.target_nodes = target_nodes

        for _ in range(num_trains):
            self._run_reinforce_train()

        return list(set(self.fired_nodes))


    def _run_reinforce_train(self):
        max_cycles = 500
        accumulated_patterns = {}
        tree_complete_counter = 0
        for _ in range(max_cycles):
            tree = self._reinforce_loop()
            if tree:
                tree_complete_counter += 1
                patterns = self._split_tree_into_patterns(tree)
                for pattern in patterns:
                    inputs, _ = self._inputs_outputs_from_pattern(pattern)
                    if pattern in accumulated_patterns:
                        accumulated_patterns[pattern] += 1
                    else:
                        accumulated_patterns[pattern] = 1
        pattern_list = [(key, accumulated_patterns[key]) for key in accumulated_patterns]
        pattern_list.sort(key=lambda item:item[1], reverse=True)
        self._process_patterns(pattern_list)


    def _process_patterns(self, pattern_list):
        patterns_wo_energy = [(self._pattern_without_energy(p[0]), p[1]) for p in pattern_list]
        patterns_wo_energy.sort(key=lambda item: item[0])
        patterns_wo_energy = list(self._accumulate(patterns_wo_energy))
        patterns_wo_energy.sort(key=lambda item: item[1], reverse=True)
        mean = patterns_wo_energy[0][1] / 2.5
        for (pattern, weight) in patterns_wo_energy:
            node = self.container.get_node_by_id(self._node_id_from_pattern(pattern))
            inputs, output = self._inputs_outputs_from_pattern(pattern)
            node.remembered_patterns.append({'inputs': inputs, 'output': output, 'rate': weight / mean})
            circuit = node.get_circuit(inputs, output)
            if circuit:
                self._upgrade_circuit(circuit, weight / mean, pattern_list, pattern)


    def _upgrade_circuit(self, circuit, weight, pattern_list, pattern):
        circuit.weight = weight
        patterns_with_energy = [p for p in pattern_list if self._pattern_without_energy(p[0]) == pattern]
        total = 0
        count = 0
        for (pattern, rate) in patterns_with_energy:
            total += int(self._energy_from_pattern(pattern)) * rate
            count += rate
        average = total / count
        circuit.firing_energy = round(average * math.sqrt(len(patterns_with_energy)))


    @staticmethod
    def _accumulate(l):
        it = itertools.groupby(l, operator.itemgetter(0))
        for key, subiter in it:
            yield key, sum(item[1] for item in subiter)


    @staticmethod
    def _pattern_without_energy(pattern):
        delimiter = pattern.find(':')
        return pattern[:delimiter - 3] + pattern[delimiter:]


    @staticmethod
    def _node_id_from_pattern(pattern):
        delimiter = pattern.find(':')
        return pattern[:delimiter]


    def _inputs_outputs_from_pattern(self, pattern):
        delimiter = pattern.find(':')
        pattern = pattern[delimiter + 1:]
        delimiter = pattern.find('-')
        nodes = []
        for node_id in pattern[:delimiter].split(','):
            nodes.append(self.container.get_node_by_id(node_id.strip()))
        output = self.container.get_node_by_id(pattern[delimiter + 1:].strip())
        return nodes, output


    @staticmethod
    def _energy_from_pattern(pattern):
        delimiter = pattern.find('(')
        return pattern[delimiter + 1:delimiter + 2].strip()


    def _split_tree_into_patterns(self, tree):
        patterns = []
        for tree_rec in tree:
            patterns.append(self._convert_to_pattern(tree_rec))
        return patterns


    @staticmethod
    def _convert_to_pattern(tree_rec):
        inputs = ', '.join([str(node.nid) for node in tree_rec['input']])
        target_nid = ''
        if tree_rec['target']:
            target_nid = tree_rec['target'].nid
        return '{}({}): {} - {}'.format(tree_rec['node'].nid, tree_rec['energy'], inputs, target_nid)


    def _reinforce_loop(self, num_trains=10):
        self.target_achieved = False
        for _ in range(num_trains):
            self._run_train()
            if self.target_achieved:
                break

        if self.target_achieved:
            # self.distribute_reward()
            return self._connection_tree(self.initial_nodes, self.target_nodes)
        return None


    def _connection_tree(self, initial_nodes, target_nodes):
        visited_connections = []
        tree = []
        for node in target_nodes:
            max_tick = node.firing_history[len(node.firing_history) - 1]['tick']
            self._connection_tree_step(node, None, tree, initial_nodes, visited_connections, max_tick)

        initial_nodes = list(initial_nodes)
        for tree_rec in tree:
            for node in tree_rec['input']:
                if node in initial_nodes:
                    idx = initial_nodes.index(node)
                    del initial_nodes[idx]
        if len(initial_nodes) == 0:
            return tree
        else:
            return None


    def _connection_tree_step(self, node, target_node, tree, initial_nodes, visited_connections, max_tick):
        history = []
        if target_node:
            firing_history = list(node.firing_history)
            firing_history.sort(key=lambda item: item['tick'], reverse=True)
            for rec in firing_history:
                if rec['tick'] <= max_tick and target_node in [c.target for c in rec['output']]:
                    history.append(rec)
                    break
        else:
            history = [rec for rec in node.firing_history if rec['tick'] == max_tick]
        for rec in history:
            rec = dict(rec)
            rec['node'] = node
            rec['target'] = target_node
            rec['output'] = [connection.target for connection in rec['output'] if connection]
            tree.append(rec)

        for incoming_node in node.input_nodes:
            conn_presentation = self._connection_presentation(incoming_node, node)
            if conn_presentation not in visited_connections and incoming_node not in initial_nodes:
                visited_connections.append(conn_presentation)
                self._connection_tree_step(incoming_node, node, tree, initial_nodes, visited_connections, max_tick - 1)


    @staticmethod
    def _connection_presentation(source, target):
        return '{} - {}'.format(source.nid, target.nid)


    def _run_train(self):
        self.reset(input_nodes=True, firing_history=True)
        self.fired_nodes.clear()
        self.fire_initials()
        self.current_tick = 0
        while self.current_tick < 20:
            self.current_tick += 1
            self.update_state()


    def fire_initials(self):
        for node in self.initial_nodes:
            node.fire_output()
            self.fired_nodes.append(node)


    def distribute_reward(self):
        visited_nodes = []
        for node in self.target_nodes:
            self._reward_node(node, None, visited_nodes)


    def _reward_node(self, node, target_node, visited_nodes):
        node.set_reward(target_node)
        visited_nodes.append(node)
        for incoming_node in node.input_nodes:
            # incoming_node = self.container.get_node_by_id(incoming_node_id)
            if incoming_node not in visited_nodes:
                self._reward_node(incoming_node, node, visited_nodes)


    def update_state(self):
        for node in self.container.nodes:
            if self.target_achieved:
                break
            node.update(self.current_tick)
            if node.fired:
                self.fired_nodes.append(node)
                if node in self.target_nodes:
                    self.target_achieved = True

        if not self.target_achieved:
            for connection in self.container.connections:
                connection.update()

