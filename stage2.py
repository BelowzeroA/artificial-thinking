import random
from clusters.network import Network


def main():

    net = Network()
    net.load_layout('./data/stage1.json')
    net.run_interactions('./data/stage2.txt')
    net.save_layout('./data/stage2.json')

    net.load_layout('./data/stage2.json')
    net.run_interactions('./data/stage2_test.txt')


def test_network():
    net = Network()
    net.run_interactions('./data/stage1.txt')
    net.save_layout('./data/stage2.json')
    return net.run_tests(verbose=False)

if __name__ == '__main__':
    main()