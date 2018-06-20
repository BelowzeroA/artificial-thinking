from clusters.connection import Connection


class Container:

    def __init__(self):
        self.nodes = []
        self.connections = []


    def get_node_by_pattern(self, pattern):
        nodes = [cl for cl in self.nodes if cl.pattern == pattern]
        if nodes:
            return nodes[0]
        return None


    def next_node_id(self):
        if len(self.nodes) == 0:
            return '1'
        return str(max([int(cl.nid) for cl in self.nodes]) + 1)


    def append_node(self, node):
        self.nodes.append(node)


    def append_connection(self, conn):
        self.connections.append(conn)


    def get_outgoing_connections(self, node):
        return [conn for conn in self.connections if conn.source == node]


    def make_connection(self, source, target):
        conn = Connection(source=source, target=target)
        self.connections.append(conn)