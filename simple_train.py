from network.neural_network import NeuralNetwork


def main():

    net = NeuralNetwork()
    net.load('./scripts/summator.json')
    # net.load('./scripts/transmission.json')
    net.fit(num_epochs=200, verbose=True)
    net.save_model('./data/summator_model.json')


if __name__ == '__main__':
    main()