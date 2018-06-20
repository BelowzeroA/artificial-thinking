

class Walker:

    def __init__(self, container):
        self.container = container
        self.initial_nodes = []
        self.current_tick = 0
        self.fired_nodes = []


    def run(self, initial_nodes):
        self.initial_nodes = initial_nodes
        self.fire_initials()
        self.current_tick = 0
        while self.current_tick < 5:
            self.current_tick += 1
            self.update_state()
        return list(set(self.fired_nodes))


    def fire_initials(self):
        for node in self.initial_nodes:
            node.fire()
            self.fired_nodes.append(node)


    def update_state(self):
        for node in self.container.nodes:
            node.update()
            if node.fired:
                self.fired_nodes.append(node)

        for connection in self.container.connections:
            connection.update()

