from typing import List

from lang.environment import Environment
from lang.scenario import Scenario


class ScenarioPetRecognition(Scenario):

    def __init__(self, environment: Environment):
        super().__init__(environment)
        self.used_utterances = []

    def respond(self, agent, inp: List[str]):
        possible_responses = ['it', 'ty', 'kiti']
        cast_dope = False
        for utterance in inp:
            utterance = utterance.replace('+', '')
            if utterance in possible_responses and utterance not in self.used_utterances:
                cast_dope = True
                self.used_utterances.append(utterance)
        if cast_dope:
            self.cast_dope(agent)