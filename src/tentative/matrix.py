import math
import random

from typing import List

ENGRAM_SIZE = 80
MATRIX_DIM = 100
MIN_DISTANCE = 10
MAX_DISTANCE = 22
INHIBITION_DISTANCE = 20


class Node:

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def _repr(self):
        return f'({self.x}, {self.y})'

    def __repr__(self):
        return self._repr()

    def __str__(self):
        return self._repr()


def generate_random_engram():
    result = []
    for _ in range(ENGRAM_SIZE):
        node = get_random_node()
        result.append(node)
    return result


def get_random_node() -> Node:
    x = random.randint(0, MATRIX_DIM - 1)
    y = random.randint(0, MATRIX_DIM - 1)
    return Node(x, y)


def get_distance_between_coords(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def get_distance(node1: Node, node2: Node) -> float:
    return get_distance_between_coords(node1.x, node1.y, node2.x, node2.y)


def allocate_joint_node(node1: Node, node2: Node) -> Node:
    while True:
        joint_node = get_random_node()
        distance1 = get_distance(joint_node, node1)
        distance2 = get_distance(joint_node, node2)
        if MIN_DISTANCE <= distance1 <= MAX_DISTANCE and MIN_DISTANCE <= distance2 <= MAX_DISTANCE:
            return joint_node


def intersect_engrams0(engram1: List[Node], engram2: List[Node]) -> List[Node]:
    result = []
    for node1 in engram1:
        for node2 in engram2:
            distance = get_distance(node1, node2)
            if MIN_DISTANCE <= distance <= MAX_DISTANCE:
                joint_node = allocate_joint_node(node1, node2)
                result.append(joint_node)
    eliminate_inhibited_nodes(result)
    return result


def intersect_engrams(engram: List[Node]) -> List[Node]:
    result = []
    for node1 in engram:
        for node2 in engram:
            if node1 == node2:
                continue
            distance = get_distance(node1, node2)
            if MIN_DISTANCE <= distance <= MAX_DISTANCE:
                joint_node = allocate_joint_node(node1, node2)
                result.append(joint_node)
    eliminate_inhibited_nodes(result)
    return result


def eliminate_inhibited_nodes(nodes: List[Node]):
    list_for_deletion = []
    for node1 in nodes:
        for node2 in nodes:
            if node1 == node2 or node1 in list_for_deletion or node2 in list_for_deletion:
                continue
            distance = get_distance(node1, node2)
            if distance <= INHIBITION_DISTANCE:
                list_for_deletion.append(node2)
    for node in list_for_deletion:
        del nodes[nodes.index(node)]


def main():
    # random.seed(150)

    sum_len = 0
    sum_derivative_len = 0
    sum_second_derivative_len = 0
    num_experiments = 10
    for _ in range(num_experiments):
        engram1 = generate_random_engram()
        engram2 = generate_random_engram()
        engram3 = generate_random_engram()
        der1 = intersect_engrams(engram1)
        der2 = intersect_engrams(engram2)
        der3 = intersect_engrams(engram3)
        second_der = intersect_engrams(der1)
        sum_second_derivative_len += len(second_der)
        sum_derivative_len += len(der1) + len(der2) + len(der3)
        intersected = intersect_engrams(der1 + der2 + der3)
        sum_len += len(intersected)
    average = sum_len // num_experiments
    average_derivative = sum_derivative_len // (num_experiments * 3)
    average_second_derivative = sum_second_derivative_len // num_experiments
    # print('engram 1:', engram1)
    # print('engram 2:', engram2)
    print(f'Source engram len: {ENGRAM_SIZE}, avg derivative: {average_derivative} avg second derivative: {average_second_derivative}')
    print(f'intersected ({len(intersected)}, avg {average}):')


if __name__ == '__main__':
    main()