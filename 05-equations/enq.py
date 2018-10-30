#!/usr/bin/env python3

import sys
from collections import OrderedDict
from numpy import linalg
import numpy as np
import re


def set_zeroes_to_missing_variables(equations_list):
    variables = []
    for equation in equations_list:
        for key, value in equation[0].items():
            if key not in variables:
                variables.append(key)

    for variable in variables:
        for equation in equations_list:
            keys = list(equation[0].keys())
            if variable not in keys:
                equation[0][variable] = 0


def get_right_coefficients(equations_list):
    result = []
    for equation in equations_list:
        result.append(int(equation[1]))

    return np.array(result)


def get_left_coefficients(equations_list):
    result = []
    for equation in equations_list:
        tmp_subresult = []
        ordered = OrderedDict(sorted(equation[0].items(), key=lambda t: t[0]))
        for key in ordered.keys():
            tmp_subresult.append(ordered[key])

        result.append(tmp_subresult)

    return np.array(result)


def get_matrix(equations_list):
    matrix = []
    for equation in equations_list:
        row = []
        ordered = OrderedDict(sorted(equation[0].items(), key=lambda t: t[0]))
        for key in ordered.keys():
            row.append(ordered[key])

        row.append(equation[1])
        matrix.append(row)

    return np.matrix(matrix)


def get_dimension(equations_list):
    return len(equations_list[0][0])


def get_variables(equations_list):
    variables = []
    ordered = OrderedDict(sorted(equations_list[0][0].items(), key=lambda t: t[0]))
    for key in ordered.keys():
        variables.append(key)

    return variables


def main():
    if len(sys.argv) != 2:
        print('Wrong number of arguments')
        print('Example: ')
        print('./enq.py input.txt')
        sys.exit(1)

    equations_list = list()
    with open(sys.argv[1], 'r') as file_stream:
        while True:
            line = file_stream.readline()
            if line is None or line is '':
                break

            splitted_by_equal = line.replace('\n', '').split('=')
            left_side = splitted_by_equal[0].replace(' ', '').replace('+', ' +').replace('-', ' -')
            # Creating well parsable format for me
            right_side = int(splitted_by_equal[1].replace(' ', ''))
            left_side_operands = left_side.split(' ')

            tmp_dict = {}
            left_side_dict = list()
            regex = re.compile(r'([\+-?]\d*)*(\w+)')

            for operand in left_side_operands:
                match = regex.match(operand)

                if match is not None:
                    value = 1
                    if match.group(1) is not None:
                        if match.group(1) == '+':
                            value = 1
                        elif match.group(1) == '-':
                            value = -1
                        else:
                            value = match.group(1)
                    tmp_dict[match.group(2)] = int(value)

            equation = (tmp_dict, right_side)

            equations_list.append(equation)

    #linalg.solve(result, y)

    # Print loaded equations
    # for equation in equations_list:
    #     print('Right side: ' + str(equation[1]))
    #     print(equation[0])

    set_zeroes_to_missing_variables(equations_list)
    # print(get_right_coefficients(equations_list))
    # print(get_left_coefficients(equations_list))

    a = get_left_coefficients(equations_list)
    b = get_right_coefficients(equations_list)

    rank_A = linalg.matrix_rank(a)
    # print('rank:')
    # print(rank_A)
    # print(get_matrix(equations_list))
    rank_entire_matrix = linalg.matrix_rank(get_matrix(equations_list))

    dimension = get_dimension(equations_list)

    # print('dimension: ' + str(dimension))
    # print(rank_A)


    if rank_A == rank_entire_matrix:
        if rank_A == dimension:
            print('solution: ', end='')
            result = linalg.solve(a, b)

            variables = get_variables(equations_list)
            for i in range(0, len(result)):
                print(str(variables[i]) + ' = ' + str(result[i]), end='')
                if i + 1 != len(result):
                    print(',',end=' ')
            print()

        if rank_A < dimension:
            print('solution space dimension: ' + str(dimension - rank_A))
    else:
        print('no solution')





    #print(np.allclose(np.dot(a, result), b))

if __name__ == '__main__':
    main()