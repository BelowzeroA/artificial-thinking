from clusters.network import Network
from clusters.builder import Builder


def main():
    builder = Builder()
    builder.build_net('data/calc_train.txt')
    builder.store('data/calc.json')

    # net = NeuralNetwork()
    # net.load('data/summator.json')
    # net.fit()


if __name__ == '__main__':
    main()