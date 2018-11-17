#!/usr/bin/env python3

import pandas as pd
import sys
import re
import json


def precount_columns(pandas_data):
    regex = re.compile(r'(\d{4}-\d{2}-\d{2})\/(\d{2})')

    deadlines = []
    dates = {}
    exercises = {}

    for key in pandas_data.keys():
        if key == 'student':
            continue

        regex_match = regex.match(key)

        if regex_match is not None:
            deadlines.append(regex_match.group(0))

            date = regex_match.group(1)
            ex = regex_match.group(2)

            # if
            if regex_match.group(1) not in dates:
                dates[regex_match.group(1)] = [regex_match.group(2)]
            else:
                dates[regex_match.group(1)].append(regex_match.group(2))

            if regex_match.group(2) not in exercises:
                exercises[regex_match.group(2)] = [regex_match.group(1)]
            else:
                exercises[regex_match.group(2)].append(regex_match.group(1))

    return deadlines, dates, exercises


def get_deadlines_stats(pandas_data, deadlines):
    deadlines_dict = {}

    for deadline in deadlines:
        deadlines_dict[deadline] = count_stats_for_column(pandas_data, deadline)


    return deadlines_dict


def get_dates_stats(pandas_data, dates):
    dates_dict = {}
    for date in dates.items():
        # print(date[0])
        tmp_dict = {}

        columns = []
        for j in date[1]:
            columns.append(date[0] + '/' + j)

        sum = 0
        for j in columns:
            sum += pandas_data[j]

        pandas_data[date[0]] = sum

        dates_dict[date[0]] = count_stats_for_column(pandas_data, date[0])


    return dates_dict


def get_exercises_stats(pandas_data, exercises):
    exercises_dict = {}
    for exercise in exercises.items():
        tmp_dict = {}

        columns = []
        for j in exercise[1]:
            columns.append(j + '/' + exercise[0])

        sum = 0
        for j in columns:
            sum += pandas_data[j]

        pandas_data[exercise[0]] = sum

        exercises_dict[exercise[0]] = count_stats_for_column(pandas_data, exercise[0])

    return exercises_dict


def count_stats_for_column(pandas_data, column_name):
    tmp_dict = {}
    tmp_dict['mean'] = pandas_data[column_name].mean()
    tmp_dict['median'] = pandas_data[column_name].median()
    tmp_dict['first'] = pandas_data[column_name].quantile(0.25)
    tmp_dict['last'] = pandas_data[column_name].quantile(0.75)
    tmp_dict['passed'] = pandas_data[pandas_data[column_name] > 0].shape[0]

    return tmp_dict


def print_output(stats):
    print(json.dumps(stats, ensure_ascii=False, indent=4))


def main():
    if sys.argv.__len__() != 3:
        print('Wrong number of arguments')
        print('Example: ')
        print('./stat.py input.txt deadlines')
        sys.exit(1)

    pandas_data = pd.read_csv(sys.argv[1], delimiter=',', skipinitialspace=True)
    # Sort columns
    pandas_data = pandas_data.reindex(sorted(pandas_data.keys()), axis=1)

    deadlines, dates, exercises = precount_columns(pandas_data)

    if sys.argv[2] == 'deadlines':
        deadlines_stats = get_deadlines_stats(pandas_data, deadlines)
        print_output(deadlines_stats)
    elif sys.argv[2] == 'dates':
        dates_stats = get_dates_stats(pandas_data, dates)
        print_output(dates_stats)
    elif sys.argv[2] == 'exercises':
        exercises_stats = get_exercises_stats(pandas_data, exercises)
        print_output(exercises_stats)
    else:
        print('Not supported option, supported: [deadlines, dates, exercises]')
        sys.exit(1)


if __name__ == '__main__':
    main()

