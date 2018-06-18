from clusters.network import Network
from clusters.builder import Builder


def main():

    net = Network()
    net.run_interactions('./data/stage1.txt')
    net.save_layout('./data/stage1.json')


if __name__ == '__main__':
    main()