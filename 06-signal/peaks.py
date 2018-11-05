#!/usr/bin/env python3

import sys
import wave
import struct
import numpy as np


def stereo_to_mono(data):
    result = []
    for i in range(0, len(data), 2):
        tmp_avg_value = (data[i] + data[i + 1]) / 2
        result.append(tmp_avg_value)

    return result


def main():
    if len(sys.argv) != 2:
        print('Wrong number of arguments')
        print('Example: ')
        print('./peaks.py audio.waw')
        sys.exit(1)

    record = wave.open(sys.argv[1], 'rb')

    num_channels = record.getnchannels()
    sample_rate = record.getframerate()
    sample_width = record.getsampwidth()
    num_frames = record.getnframes()

    record_data = record.readframes(num_frames)

    total_samples = num_frames * num_channels


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

    low = np.inf
    high = - np.inf

    for i in range(0, windows_count):
        tmp_fft_window = np.abs(np.fft.rfft(data[i * sample_rate:i*sample_rate+sample_rate]))

        tmp_sum = 0
        for value in tmp_fft_window:
            tmp_sum += np.abs(value)

        average_value = tmp_sum / len(tmp_fft_window)

        for index in range(0, len(tmp_fft_window)):
            if tmp_fft_window[index] >= 20 * average_value:
                if index < low:
                    low = index
                if index > high:
                    high = index

    if low == np.inf and high == -np.inf:
        print('no peaks')
    else:
        print('low = {0}, high = {1}'.format(low, high))


if __name__ == '__main__':
    main()
    