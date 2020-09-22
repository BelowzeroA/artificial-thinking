from lang.environment import Environment


class Scenario:

    def __init__(self, environment: Environment):
        self.environment = environment

    def respond(self, inp: str):
        raise NotImplementedError('respond() must be overriden in descendant classes')

    def cast_dope(self, agent):
        self.environment.spread_dope(agent)