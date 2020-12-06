from typing import List

from lang.agent import Agent
from lang.environment import Environment
from lang.scenario import Scenario


class ScenarioPetRecognition(Scenario):

    def __init__(self, environment: Environment):
        super().__init__(environment)
        self.used_utterances = []

    def respond(self, agent: Agent, inp: List[str]):
        assembly_source = agent.current_assembly_source()
        if not assembly_source.patterns_to_be_rewarded:
            return
        # possible_responses = ['it', 'ty', 'kiti']
        cast_dope = False
        for utterance in inp:
            utterance = utterance.replace('+', '')
            if utterance in assembly_source.patterns_to_be_rewarded and utterance not in self.used_utterances:
                cast_dope = True
                self.used_utterances.append(utterance)
        if cast_dope:
            self.cast_dope(agent)