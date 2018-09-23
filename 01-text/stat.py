#!/usr/bin/env python3

import sys
import re
from collections import Counter


def get_century_from_year(year):
    return int(year) // 100 + 1


def count_pieces_by_composers(file):
    composer_regex = re.compile(r"Composer: (.*)")

    result = Counter()

    file.seek(0)
    for i in file:
        composers = composer_regex.match(i)

        if composers is not None:
            composers_in_array = composers.group(1).split(";")

            for j in composers_in_array:
                tmp_composer = re.sub(r"\(.*\)", '', j)
                tmp_composer = re.sub(r"\s*$", '', tmp_composer)
                tmp_composer = re.sub(r"^\s*", '', tmp_composer)

                if tmp_composer != '':
                    result[tmp_composer] += 1

    return result


def count_pieces_by_centuries(file):
    composition_year_regex = re.compile(r"Composition Year: (.*)")
    century_regex = re.compile(r"(\d*)th century")
    year_regex = re.compile(r"(\d{4})")

    result = Counter()

    file.seek(0)
    for i in file:
        composition_year = composition_year_regex.match(i)

        if composition_year is not None:
            century = century_regex.match(composition_year.group(1))

            if century is not None:
                result[century.group(1)] += 1
            else:
                year = year_regex.search(composition_year.group(1))

                if year is not None:
                    result[str(get_century_from_year(year.group(1)))] += 1

    return result


def print_composers(counter):
    for item in counter:
        print(item + ': ' + str(counter[item]))


def print_centuries(counter):
    for item in counter:
        print(str(item) + 'th century: ' + str(counter[item]))


def main():

    if len(sys.argv) != 3 or sys.argv[2] not in ['composer', 'century']:
        print('Wrong arguments given')
        print('Use:')
        print('./stat.py ./file_path composer')
        print('or')
        print('./stat.py ./file_path century')

        sys.exit(1)

    file_path = sys.argv[1]
    composers_or_centuries = sys.argv[2]

    file = open(file_path, 'r', encoding='utf8')

    if composers_or_centuries == 'composer':
        print_composers(count_pieces_by_composers(file))

    if composers_or_centuries == 'century':
        print_centuries(count_pieces_by_centuries(file))


if __name__ == '__main__':
    main()

