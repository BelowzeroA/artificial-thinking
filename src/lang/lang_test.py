import random

from lang import configs
from lang.agent import Agent
from lang.environment import Environment


def main():
    random.seed(24)

    config = configs.MainConfig.__dict__

    env = Environment(**config)
    env.verbosity = 0
    agent = Agent(environment=env, **config)
    env.add_agent(agent)
    env.run()


if __name__ == '__main__':
    main()