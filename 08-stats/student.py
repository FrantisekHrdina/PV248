#!/usr/bin/env python3
from datetime import date, timedelta, datetime
from math import ceil
from operator import itemgetter

import pandas as pd
import sys
import re
import json
import numpy as np


def get_list_of_students_ids(pandas_data):
    ids = []

    for i in pandas_data['student']:
        ids.append(i)

    ids.sort(reverse=False)

    return ids


def precount_columns(pandas_data):
    regex = re.compile(r'(\d{4}-\d{2}-\d{2})\/(\d{2})')

    exercises = {}
    dates = {}
    deadlines = []

    for key in pandas_data.keys():
        if key == 'student':
            continue

        regex_match = regex.match(key)

        if regex_match is not None:
            deadlines.append(regex_match.group(0))

            if regex_match.group(2) not in exercises:
                exercises[regex_match.group(2)] = [regex_match.group(1)]
            else:
                exercises[regex_match.group(2)].append(regex_match.group(1))

            if regex_match.group(1) not in dates:
                dates[regex_match.group(1)] = [regex_match.group(2)]
            else:
                dates[regex_match.group(1)].append(regex_match.group(2))

    return exercises, dates, deadlines


def points_predictor(student_stats, dates):
    # x_dates = []
    # x_dates.append(0)
    # x_dates.extend(np.arange(8, 7 * len(dates) + 2, 7))
    #
    # print(x_dates)

    # Start date is the begging of the semester
    start_date = datetime.strptime('2018-09-17', '%Y-%m-%d').date()

    y_points = []
    y_current_sum = 0
    #y_points.append(0)

    # generate x
    x_dates = []
    #x_dates.append(0)


    for date_i in dates.items():
        tmp_date = datetime.strptime(date_i[0], '%Y-%m-%d').date()
        diff = tmp_date - start_date
        x_dates.append(diff.days)

    # print(x_dates)
    #TODO setřídit data podle datumů
    #dates = sorted(dates, key=dates.__getitem__)
    # df = df.reindex(sorted(df.columns), axis=1)
    for date_i in dates.items():
        columns = []

        for j in date_i[1]:
            columns.append(date_i[0] + '/' + j)

        sum = 0

        for j in columns:
            sum += student_stats[j].iloc[0]

        y_points.append(y_current_sum + sum)
        y_current_sum += sum


    # print(y_points)
    # A = np.array([x_dates, np.ones(x_dates.__len__())])


    sum_xy=0
    sum_x_square =0
    for i in range(0, len(x_dates)):
        sum_xy += x_dates[i] * y_points[i]
        sum_x_square += x_dates[i] * x_dates[i]

    # print(sum_xy/sum_x_square)

    k_slope = sum_xy / sum_x_square

    # y = kx + q

    # result = np.linalg.lstsq(A.T, y_points, rcond=None)[0]
    #
    # k_slope = result[0]

    # q shift should be ignored according to the assignment
    # q_shift = result[1]

    if k_slope != 0:
        q_shift = 0
        x_points_16 = (16 - q_shift) / k_slope
        x_points_20 = (20 - q_shift) / k_slope

        date_for_16_points = start_date + timedelta(x_points_16)
        date_for_20_points = start_date + timedelta(x_points_20)

    else:
        date_for_20_points = None
        date_for_16_points = None

    return date_for_16_points, date_for_20_points, k_slope


def count_average_student(pandas_data):
    result = pandas_data[pandas_data.keys()].mean()
    result = result.to_frame().T

    return result


def print_output(result):
    print(json.dumps(result, ensure_ascii=False, indent=4))


def prepare_json(student_stats, dates, exercises_list):
    result = {}
    result['mean'] = student_stats[exercises_list].mean(axis=1).iloc[0]
    result['median'] = student_stats[exercises_list].median(axis=1).iloc[0]
    result['total'] = student_stats[exercises_list].sum(axis=1).iloc[0]
    result['passed'] = int(student_stats[student_stats[exercises_list] > 0].count(axis=1).iloc[0])

    date_for_16_points, date_for_20_points, slope = points_predictor(student_stats, dates)

    result['regression slope'] = slope
    if slope != 0:
        result['date 16'] = date_for_16_points.strftime('%Y-%m-%d')
        result['date 20'] = date_for_20_points.strftime('%Y-%m-%d')

    return result


def main():
    if sys.argv.__len__() != 3:
        print('Wrong number of arguments')
        print('Example: ')
        print('./stat.py input.txt deadlines')
        sys.exit(1)

    pandas_data = pd.read_csv(sys.argv[1], delimiter=',', skipinitialspace=True)

    # Sort columns
    pandas_data = pandas_data.reindex(sorted(pandas_data.keys()), axis=1)
    exercises, dates, deadlines = precount_columns(pandas_data)

    # add count sum for exercises
    for exercise in exercises.items():
        columns = []

        for j in exercise[1]:
            columns.append(j + '/' + exercise[0])

        sum = 0
        for j in columns:
            sum += pandas_data[j]

        pandas_data[exercise[0]] = sum

    student_id = sys.argv[2]

    exercises_list = []
    for exercise in exercises:
        exercises_list.append(exercise)

    if student_id == 'average':
        average_student = count_average_student(pandas_data)
        output = prepare_json(average_student, dates, exercises_list)
        print_output(output)
    elif student_id == 'all':
        # Testing output
        ids = get_list_of_students_ids(pandas_data)

        for i in ids:
            print(str(i) + ':')
            student_stats = pandas_data.loc[pandas_data['student'] == int(i)]
            output = prepare_json(student_stats, dates, exercises_list)
            print_output(output)
            print()

    else:
        student_stats = pandas_data.loc[pandas_data['student'] == int(student_id)]
        output = prepare_json(student_stats, dates, exercises_list)
        print_output(output)




if __name__ == '__main__':
    main()
