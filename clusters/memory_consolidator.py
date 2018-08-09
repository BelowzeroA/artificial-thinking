from clusters.network_runner import NetworkRunner


class MemoryConsolidator(NetworkRunner):
    """
    Network runner that works when the "baby" sleeps
    Runs "memory consolidation" mode
    Creates supplemental abstract nodes and connections between common neighbours
    """
    def __init__(self, container):
        super().__init__(container=container)
        self.container.consolidation_mode = True
        self.fired_nodes = []
        self.fired_nodes_counter = {}
        self.pulsed_connections_counter = {}


    def run(self):
        self.reset()
        self.fired_nodes_counter.clear()
        self.initial_nodes = [node for node in self.container.nodes if node.is_episode]
        self.fire_initials()
        self.current_tick = 0
        while self.current_tick < 40:
            self.current_tick += 1
            self.update_state(self.current_tick)
        return self.fired_nodes_counter, self.pulsed_connections_counter


    def fire_initials(self):
        for node in self.initial_nodes:
            node.fire()
            node.firing = True
            self.fired_nodes.append(node)


    def _handle_fired_node(self, node):
        self.fired_nodes.append(node)
        node.fired = False
        if node in self.fired_nodes_counter:
            self.fired_nodes_counter[node] += 1
        else:
            self.fired_nodes_counter[node] = 1
        for conn in node.causal_connections:
            if conn in self.pulsed_connections_counter:
                self.pulsed_connections_counter[conn] += 1
            else:
                self.pulsed_connections_counter[conn] = 1


    def update_state(self, current_tick):
        for node in self.container.nodes:
            node.update(current_tick)
            if node.fired:
                self._handle_fired_node(node)
            node.causal_connections.clear()

        for connection in self.container.connections:
            connection.update()

