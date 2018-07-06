

class NetworkRunner:

    def __init__(self, container):
        self.container = container
        self.initial_nodes = []
        self.current_tick = 0
        self.fired_nodes = []


    def reset(self):
        for conn in self.container.connections:
            conn.pulsed = False
            conn.pulsing = False
        for node in self.container.nodes:
            node.fired = False
            node.firing = False
            node.potential = 0

