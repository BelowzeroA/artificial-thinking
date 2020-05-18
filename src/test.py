import math
import os
import random
import re
import sys
from collections import Counter


# Complete the sockMerchant function below.
def sockMerchant(n, ar):
    cntr = dict(Counter(ar))
    pairs = 0
    for key in cntr:
        pairs += int(cntr[key] / 2)
    return pairs

if __name__ == '__main__':

    n = int(input())

    ar = list(map(int, input().rstrip().split()))

    result = sockMerchant(n, ar)

    print(result)
