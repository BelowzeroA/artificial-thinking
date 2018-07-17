from clusters.network_runner import NetworkRunner


class Walker(NetworkRunner):

    def __init__(self, container):
        super().__init__(container)
        self.container.reinforcement_mode = False


    def run(self, initial_nodes, max_ticks=5):
        self.reset()
        self.initial_nodes = initial_nodes
        self.fire_initials()
        self.current_tick = 0
        while self.current_tick < max_ticks:
            self.current_tick += 1
            self.update_state()
        return list(set(self.fired_nodes))


    def fire_initials(self):
        for node in self.initial_nodes:
            node.fire()
            self.fired_nodes.append(node)


    def reset(self):
        for node in self.container.nodes:
            node.fired = False
            node.firing = False
            node.potential = 0


    def update_state(self):
        for node in self.container.nodes:
            node.update(self.current_tick)
            if node.fired:
                self.fired_nodes.append(node)

        for connection in self.container.connections:
            connection.update()

