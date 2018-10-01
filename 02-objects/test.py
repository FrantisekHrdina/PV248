#!/usr/bin/env python3

import sys

from scorelib import *
import scorelib

def main():
    if len(sys.argv) != 2:
        print('Wrong number of arguments')
        print('Example: ')
        print('./test.py scorelib.txt')

    prints_list = load(sys.argv[1])
    for item in prints_list:
        item.format()
        print()


if __name__ == '__main__':
    main()
