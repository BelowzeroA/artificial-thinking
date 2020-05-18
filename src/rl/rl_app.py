import math

from clusters.container import Container
from clusters.node import Node
from clusters.reinforce_trainer import ReinforceTrainer
from clusters.urge_resolver import UrgeResolver
from clusters.walker import Walker
from rl.agent import Agent
from utils.file_ops import load_list_from_file
from utils.json_serializer import json_serialize
from utils.misc import split_list_in_batches


class RLApp:
    """
    The main entry point and the manager of all neural processes
    """
    def __init__(self, world, num_agents=1):
        self.container = Container()
        self.world = world
        self.current_tick = 0
        self.input_nodes = []
        self.agents = []
        self.log = []
        self._init_agents(num_agents=num_agents)


    def _init_agents(self, num_agents):
        for i in range(num_agents):
            agent = Agent(self.world)
            self.agents.append(agent)


    def load_layout(self, filename):
        self.container.load(filename)


    @staticmethod
    def print_log(log):
        for log_line in log:
            print(log_line)


    def run(self, epochs=10):
        """
        Performs running cycle
        :param filename:
        :return:
        """
        for i in range(epochs):
            self._run_epoch()


    def _reset_agents(self):
        for agent in self.agents:
            agent.x_coord = self.world.hive_x
            agent.y_coord = self.world.hive_y
            agent.reset()


    def _run_epoch(self):
        iters = 200
        self._reset_agents()
        overall_reward = 0
        for i in range(iters):
            for agent in self.agents:
                reward = agent.act()
                overall_reward += reward
        print('overall reward', overall_reward)

