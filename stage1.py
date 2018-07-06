import random
from clusters.network import Network


# random.seed(43)


def main():
    net = Network()
    net.run_interactions('./data/stage1.txt')
    net.sleep()
    net.save_layout('./data/stage1.json')

    # net.run_tests(verbose=False)
    # success = 0
    # iter_count = 1
    # for i in range(iter_count):
    #     result = test_network()
    #     if result:
    #         success += 1
    #
    # print('test accuracy: {}%'.format(success / iter_count * 100))


def test_network():
    net = Network()
    net.run_interactions('./data/stage1.txt')
    net.save_layout('./data/stage1.json')
    return net.run_tests(verbose=False)

if __name__ == '__main__':
    main()