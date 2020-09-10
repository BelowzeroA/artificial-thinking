import importlib

from common.file_ops import load_list_from_file
from lang.configs import SCENARIO_PREFIX


class Environment:

    def __init__(self, **config):
        self.config = config
        self.filename = config.get('environment_scenario_path')
        self.load()
        self.utterances = []
        self.agents = []
        self.loop_ended = False
        self.current_tick = 0
        self._scenarios = []
        # how many ticks the scenario will take
        self.scenario_length = 0
        self._load_scenarios()

    def load(self):
        lines = load_list_from_file(self.filename)

    def _load_scenarios(self):
        lines = load_list_from_file(self.filename)
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # colon_ind = line.index(':')
            # index = int(line[:colon_ind])
            # content = line[colon_ind + 1:].strip()
            if not line.startswith(SCENARIO_PREFIX):
                continue
            scenario_name = line[3:].strip()
            scenario_class_name = f'Scenario{scenario_name}'
            module_name = f'lang.scenarios.scenario_{scenario_name.lower()}'
            scenario_class = getattr(importlib.import_module(module_name), scenario_class_name)
            scenario = scenario_class(self)
            self._scenarios.append(scenario)

    def add_agent(self, agent):
        self.agents.append(agent)

    def receive_utterance(self, utterance: str):
        print(f'Agent said: {utterance}')
        self.utterances.append(utterance)

    def reset_agents(self):
        for agent in self.agents:
            agent.reset()

    def update_agents(self):
        for agent in self.agents:
            agent.update()

    def spread_dope(self):
        pass

    def interact_with_agents(self):
        if self.utterances:
            for scenario_start_tick in self._scenarios:
                if self.current_tick >= scenario_start_tick:
                    scenario = self._scenarios[scenario_start_tick]
                    scenario.respond(self.utterances)
            # for utterance in self.utterances:
            #     if utterance in ['ki', 'ti']:
            #         self.spread_dope()

    def run(self, max_ticks=100):
        self.loop_ended = False
        result = False
        self.current_tick = 0
        self.reset_agents()
        while self.current_tick <= self.scenario_length and not self.loop_ended:
            self.current_tick += 1
            print('Tick {}'.format(self.current_tick))
            self.update_agents()
            self.interact_with_agents()
        return result

