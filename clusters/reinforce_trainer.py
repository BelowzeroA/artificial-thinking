from clusters.network_runner import NetworkRunner


class ReinforceTrainer(NetworkRunner):

    def __init__(self, container):
        super().__init__(container=container)
        self.container.reinforcement_mode = True
        self.fired_nodes = []
        self.target_nodes = []
        self.target_achieved = False


    def run(self, initial_nodes, target_nodes):
        self._clear_state()
        self.initial_nodes = initial_nodes
        self.target_nodes = target_nodes
        self.fire_initials()
        self.current_tick = 0
        while self.current_tick < 40:
            self.current_tick += 1
            self.update_state()
        if self.target_achieved:
            self.distribute_reward()
        return list(set(self.fired_nodes))


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
        for incoming_node_id in node.input_nodes:
            incoming_node = self.container.get_node_by_id(incoming_node_id)
            if incoming_node not in visited_nodes:
                self._reward_node(incoming_node, node, visited_nodes)


    def update_state(self):
        for node in self.container.nodes:
            if self.target_achieved:
                break
            node.update()
            if node.fired:
                self.fired_nodes.append(node)
                if node in self.target_nodes:
                    self.target_achieved = True

        if not self.target_achieved:
            for connection in self.container.connections:
                connection.update()

