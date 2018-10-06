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

    #tmp_print = Print()
    # tmp_print = prints_list[-1]
    # print(tmp_print.print_id)
    # print()


if __name__ == '__main__':
    main()
