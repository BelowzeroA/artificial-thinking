import os

root_path = None


def load_list_from_file(filename):
    lines = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            lines.append(line.strip())
    return lines


def path_from_root(dirname: str) -> str:
    """
    Returns a project root path joined with :param dirname:
    The project root is considered the first directory containing 'requirements.txt'
    :param dirname: path to join with
    :return:
    """
    global root_path
    if root_path:
        return os.path.join(root_path, dirname)
    path = os.path.normpath(__file__)
    max_levels_up = 3
    counter = 0
    while path and counter < max_levels_up:
        parts = os.path.split(path)
        preceeding_part = parts[0]
        tried_filename = os.path.join(preceeding_part, 'requirements.txt')
        if os.path.exists(tried_filename):
            root_path = preceeding_part
            return os.path.join(preceeding_part, dirname)
        path = preceeding_part
        counter += 1
        if counter >= max_levels_up:
            root_path = preceeding_part
            return os.path.join(preceeding_part, dirname)
    return ''