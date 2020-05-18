import os

from common.file_ops import path_from_root


data_dir = path_from_root('data/lang')


SCENARIO_PREFIX = 'sc:'


class MainConfig:
    phonetics_path = os.path.join(data_dir, 'phonetics_eng.txt')
    # environment_scenario_path = os.path.join(data_dir, 'env_debug_ph_rec_zone.txt')
    environment_scenario_path = os.path.join(data_dir, 'sc_all_about_kitty.txt')