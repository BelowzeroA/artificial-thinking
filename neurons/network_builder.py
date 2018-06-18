from neurons.neuro_container import NeuroContainer
from neurons.clump import Clump
from utils.json_serializer import json_serialize


class NetworkBuilder:

    def __init__(self):
        self.nodes = []
        self.stop_words = ['a', 'is', 'in']
        self.container = NeuroContainer()


    def load_list_from_file(filename):
        lines = []
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                lines.append(line.strip())
        return lines


    def build_net(self, filename):
        lines = Builder.load_list_from_file(filename)
        for line in lines:
            nodes = []
            tokens = line.split()
            for token in tokens:
                if token in self.stop_words:
                    continue
                clump = self._check_make_clump(token)
            #     if node not in nodes:
            #         nodes.append(node)
            # if len(nodes) > 2:
            #     self._make_clump(nodes)


    def _check_make_clump(self, token):
        clump = self.container.get_clump_by_pattern(token)
        if not clump:
            clump = Clump(self.container.next_clump_id(), pattern=token, container=self.container, abstract=False)
            clump.allocate_neurons()
            self.container.append_clump(clump)
        return clump


    def store(self, filename):
        out_val = {'clumps': self.container.clumps,
                   'neurons': self.container.neurons,
                   'synapses': self.container.synapses}
        with open(filename, mode='wt', encoding='utf-8') as output_file:
            print(json_serialize(out_val), file=output_file)



