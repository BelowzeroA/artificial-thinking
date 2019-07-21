from clusters.network_runner import NetworkRunner


class UrgeResolver(NetworkRunner):

    def __init__(self, container, log):
        super().__init__(container=container)
        self.container.urge_mode = True
        self.result_nodes = []
        self.urge_resolved = False
        self.log = log


    def run(self, initial_nodes):
        self.initial_nodes = initial_nodes
        self._run_train()
        if self.urge_resolved:
            pass
        return list(set(self.result_nodes))


    def _run_train(self):
        self.reset(input_nodes=True)
        self.fire_initials()
        self.current_tick = 0
        while self.current_tick < 20:
            self.current_tick += 1
            self.update_state()


    def fire_initials(self):
        for node in self.initial_nodes:
            node.potential = 1
            self.fired_nodes.append(node)


    def update_state(self):
        for node in self.container.nodes:
            if self.urge_resolved:
                break
            node.update(self.current_tick, self.log)
            if node.fired and node.is_synthesizer():
                self.urge_resolved = True
                self.result_nodes.append(node)

        if not self.urge_resolved:
            for connection in self.container.connections:
                connection.update()

