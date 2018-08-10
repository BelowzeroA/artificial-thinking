from clusters.network import Network


def main():

    net = Network()
    net.load_layout('./data/stage1.json')
    net.run_interactions('./data/stage2.txt')
    net.save_layout('./data/stage2.json')

    net.load_layout('./data/stage2.json')
    result = net.run_interactions('./data/stage2_test.txt')
    for batch in result:
        print('{}: {}'.format(batch, result[batch]))


if __name__ == '__main__':
    main()