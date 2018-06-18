

class Walker:

    def __init__(self, container):
        self.container = container
        self.initial_nodes = []
        self.current_tick = 0


    def run(self, initial_nodes):
        self.initial_nodes = initial_nodes
        self.current_tick = 0
        while self.current_tick < 5:
            self.current_tick += 1
            self.update_state()


    def update_state(self):
        for node in self.container.nodes:
            node.update()
        for connection in self.container.connections:
            connection.update()

