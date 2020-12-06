


def biggest_odd_divisor(n: int):
    if n % 2 == 1:
        return n
    else:
        return biggest_odd_divisor(int(n / 2))


if __name__ == '__main__':
    sum = 0
    for i in range(111, 220):
        divisor = biggest_odd_divisor(i)
        print(f'{i}: {divisor}')
        sum += divisor
    print(sum)
