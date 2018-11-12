#!/usr/bin/env python3

import sys
import wave
import struct
import numpy as np
from operator import itemgetter
from math import log2, log


def stereo_to_mono(data):
    result = []
    for i in range(0, len(data), 2):
        tmp_avg_value = (data[i] + data[i + 1]) / 2
        result.append(tmp_avg_value)

    return result


def get_three_max_peaks(data, start, end):
    peaks = []

    tmp_fft_window = np.abs(np.fft.rfft(data[start:end]))
    tmp_sum = 0
    for value in tmp_fft_window:
        tmp_sum += np.abs(value)

    average_value = tmp_sum / len(tmp_fft_window)

    for index in range(0, len(tmp_fft_window)):
        if tmp_fft_window[index] >= 20 * average_value:
            peaks.append((index, tmp_fft_window[index]))

    peaks.sort(key=itemgetter(1), reverse=True)

    clusters = []
    # For merging peaks that are next to eeach other in range 1Hz
    merge_border = 1

    # Sorted by frequencies ASC
    peaks.sort(key=itemgetter(0), reverse=False)

    # print(peaks)

    i = 0
    while i < len(peaks):
        tmp_cluster = []
        # [0] frequence on which max value is
        # [1] max value of peak
        # [2] list of all peaks that belongs to cluster

        tmp_cluster.append(peaks[i][0])
        tmp_cluster.append(peaks[i][1])
        tmp_cluster.append([peaks[i]])

        if i + 1 < len(peaks):
            while np.abs(peaks[i][0] - peaks[i + 1][0]) <= merge_border:
                if peaks[i + 1][1] > tmp_cluster[1]:
                    tmp_cluster[1] = peaks[i + 1][1]
                    tmp_cluster[0] = peaks[i+1][0]
                tmp_cluster[2].append(peaks[i+1])
                i += 1
                if i + 1 == len(peaks):
                    break

        clusters.append(tmp_cluster)

        i +=1

    # Sorted by max value of peak DESC
    clusters.sort(key=itemgetter(1), reverse=True)

    three_max_clusters = []

    for i in range(0, len(clusters)):
        three_max_clusters.append((clusters[i][0], clusters[i][1]))
        if three_max_clusters.__len__() == 3:
            break

    return three_max_clusters


    # for peak_freq, peak_value in peaks:
    #     # if clustered_peaks.__len__() == 0:
    #     #     clustered_peaks.append((peak_freq, peak_value))
    #     #     value = clustered_peaks.sort(key=itemgetter(0), reverse=True)
    #     # else:
    #     #     if np.abs(clustered_peaks[-1][0] - peak_freq) <= merge_border:
    #     #         if clustered_peaks[-1][1] < peak_value:
    #     #             clustered_peaks[-1] = (peak_freq, peak_value)
    #     #     else:
    #     #         clustered_peaks.append((peak_freq, peak_value))
    #     #         value = clustered_peaks.sort(key=itemgetter(0), reverse=True)
    #
    #     if clustered_peaks.__len__() == 0:
    #         clustered_peaks.append((peak_freq, peak_value))
    #     elif clustered_peaks.__len__() == 1:
    #         if np.abs(clustered_peaks[-1][0] - peak_freq) <= merge_border:
    #             if clustered_peaks[-1][1] < peak_value:
    #                 clustered_peaks[-1] = (peak_freq, peak_value)
    #         else:
    #             clustered_peaks.append((peak_freq, peak_value))
    #
    #     elif clustered_peaks.__len__() == 2:
    #         if np.abs(clustered_peaks[-1][0] - peak_freq) <= merge_border:
    #             if clustered_peaks[-1][1] < peak_value:
    #                 clustered_peaks[-1] = (peak_freq, peak_value)
    #
    #         elif np.abs(clustered_peaks[-2][0] - peak_freq) <= merge_border:
    #             if clustered_peaks[-2][1] < peak_value:
    #                 clustered_peaks[-2] = (peak_freq, peak_value)
    #
    #         else:
    #             clustered_peaks.append((peak_freq, peak_value))
    #
    #     if clustered_peaks.__len__() == 3:
    #         break
    #
    # return clustered_peaks


def get_freqs_from_peaks_array(peaks):
    freqs = []

    for freq, value in peaks:
        freqs.append(freq)

    return freqs


def windows_in_same_segment_check(current, next):
    current_freqs = get_freqs_from_peaks_array(current)
    next_freqs = get_freqs_from_peaks_array(next)

    # windows belongs to segment if their three max peaks frequencies are equal

    if current_freqs.__len__() != next_freqs.__len__():
        return False

    for next_freq in next_freqs:
        if next_freq not in current_freqs:
            return False

    return True


def count_segments(sliding_windows):
    segments = []

    windows_count = sliding_windows.__len__()
    i = 0
    while i + 1 < windows_count:

        current_win = sliding_windows[i]
        next_win = sliding_windows[i + 1]

        start = i
        end = i
        while windows_in_same_segment_check(current_win, next_win) and i + 2 < windows_count:
            end = i + 1
            current_win = sliding_windows[i + 1]
            next_win = sliding_windows[i + 2]
            i += 1

        if i + 2 == windows_count:
            if windows_in_same_segment_check(sliding_windows[i], sliding_windows[i + 1]):
                tmp_segment = (start / 10, (end + 2) / 10, get_freqs_from_peaks_array(sliding_windows[i]))
                segments.append(tmp_segment)
            else:
                tmp_segment = (start / 10, (end + 1) / 10, get_freqs_from_peaks_array(sliding_windows[i]))
                start += 1
                end += 1
                tmp_segment2 = (start / 10, (end + 1) / 10, get_freqs_from_peaks_array(sliding_windows[i+1]))
                segments.append(tmp_segment)
                segments.append(tmp_segment2)
        else:
            tmp_segment = (start / 10, (end + 1) / 10, get_freqs_from_peaks_array(sliding_windows[i]))
            segments.append(tmp_segment)
        i = i + 1

    return segments


def print_segments(segments, base_a4_freq):
    for segment in segments:
        # print('{0}-{1}'.format(segment[0], segment[1]), end='')
        # segment[2].sort(key=int, reverse=False)
        # for pitch_freq in segment[2]:
        #     print(' ' + get_pitch_from_freq(pitch_freq, base_a4_freq), end='')
        # print()
        #

        if segment[2].__len__() != 0:
            print('{0}-{1}'.format(segment[0], segment[1]), end='')
            segment[2].sort(key=int, reverse=False)
            for pitch_freq in segment[2]:
                print(' ' + get_pitch_from_freq(pitch_freq, base_a4_freq), end='')
            print()


def get_pitch_from_freq(frequency, base_a4_freq):
    C0 = base_a4_freq * 2 ** (-4.75)
    pitches = ['c', 'cis', 'd', 'es', 'e', 'f', 'fis', 'g', 'gis', 'a', 'bes', 'b']


    # cents = 1200 * (log(frequency/base_a4_freq)/log(2))

    diff_in_steps = round(12* log2(frequency/C0))

    # h2 = 12* log2(frequency/C0)

    note_frequency = 2 ** (diff_in_steps * 100 / 1200) * C0

    diff_in_cents = 1200*(log(frequency/note_frequency)/log(2))

    octave = diff_in_steps // 12
    n = diff_in_steps % 12

    pitch = pitches[n]

    if octave == 0:
        pitch = pitch.title() + ',,'
    elif octave == 1:
        pitch = pitch.title() + ','
    elif octave == 2:
        pitch = pitch.title()
    elif octave == 3:
        pitch = pitch
    elif octave == 4:
        pitch = pitch + "’"
    elif octave == 5:
        pitch = pitch + "’’"
    elif octave == 6:
        pitch = pitch + "’’’"
    elif octave == 7:
        pitch = pitch + "’’’’"
    elif octave == 8:
        pitch = pitch + "’’’’’"
    elif octave == 9:
        pitch = pitch + "’’’’’’"
    elif octave == 10:
        pitch = pitch + "’’’’’’’"

    if np.abs(diff_in_cents) >= float(1):
        string_diff = str(round(diff_in_cents))
        if not string_diff.startswith('-'):
            string_diff = '+' + string_diff
    else:
        string_diff = '+0'

    pitch = pitch + string_diff

    return pitch


def main():
    if len(sys.argv) != 3:
        print('Wrong number of arguments')
        print('Example: ')
        print('./music.py 440 audio.waw')
        sys.exit(1)

    base_a4_freq = int(sys.argv[1])
    record = wave.open(sys.argv[2], 'rb')

    num_channels = record.getnchannels()
    sample_rate = record.getframerate()
    sample_width = record.getsampwidth()
    num_frames = record.getnframes()

    record_data = record.readframes(num_frames)

    total_samples = num_frames * num_channels

    # print(num_frames/sample_rate)


    # format for unsigned
    #fmt = "%iB" % total_samples

    # format for signed
    fmt = "%ih" % total_samples

    data = struct.unpack(fmt, record_data)

    if num_channels == 2:
        # Stereo to Mono, get average from both channels
        tmp_data = stereo_to_mono(data)
        data = tmp_data

    windows_count = len(data) // sample_rate

    sample_rate = sample_rate

    end = sample_rate
    start = 0
    step = sample_rate // 10

    sliding_windows = []
    while end <= len(data):
        sliding_windows.append(get_three_max_peaks(data, start, end))
        start += step
        end += step

    segments = count_segments(sliding_windows)

    print_segments(segments, base_a4_freq)

    # print(get_pitch_from_freq(448, base_a4_freq))
    # print(get_pitch_from_freq(19900, base_a4_freq))
    # print(get_pitch_from_freq(115, base_a4_freq))
    # print(get_pitch_from_freq(842, base_a4_freq))
    # print(get_pitch_from_freq(20, base_a4_freq))


if __name__ == '__main__':
    main()
