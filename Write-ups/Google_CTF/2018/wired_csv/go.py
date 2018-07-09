import csv
from operator import itemgetter
from bisect import bisect_right

import numpy as np
import matplotlib.pyplot as plt

wires = None

def converter():
    """Parse csv into numpy array"""
    with open('data.csv') as fp:
        data = csv.reader(fp, delimiter=',', skipinitialspace=True)
        next(data)  # skip first line

        wires = [[] for _ in range(8)]
        for line in data:
            for wire_no in range(8):
                line_index = wire_no * 2 + 3
                if line[line_index]:
                    wires[wire_no].append(
                        (
                            float(line[line_index]),
                            int(line[line_index + 1])
                        )
                    )

    for wire_no in range(8):
        wires[wire_no] = np.array(
            wires[wire_no],
            dtype=[
                ('time', np.float32),
                ('val', np.int16)
            ]
        )
    wires = np.array(wires)

    np.save('data.npy', wires)


def find_value(wire_no, x):
    place = np.searchsorted(wires[wire_no]['time'], x, side='left')
    try:
        return wires[wire_no][place]['val']
    except IndexError:
        return wires[wire_no][place - 1]['val']


def demultiplex(time):
    n1 = 0
    n1 += (not find_value(0, time)) * 1
    n1 += (not find_value(1, time)) * 2
    n1 += (not find_value(2, time)) * 4
    n2 = 0
    n2 += (not find_value(3, time)) * 1
    n2 += (not find_value(4, time)) * 2
    n2 += (not find_value(5, time)) * 4

    return n1, n2


CONVERTER_1 = [16, 15, 12, 17, 10, 14, 11, 13]
CONVERTER_2 = [6, 1, 4, 7, 2, 8, 3, 5]
MATRIX = [
    ['*brk*', '7', '*Nil*', '8', '9', '0', '<', '>', '*del*'],
    ['*Nil*', '6', '*Nil*', '5', '4', '3', '2', '1', '*esc*'],
    ['*Nil*', 'u', '*Nil*', 'i', 'o', 'p', '-', '=', '*ret*'],
    ['*Nil*', 'y', '*Nil*', 't', 'r', 'e', 'w', 'q', '*tab*'],
    ['*Ctl*', '*Nil*', 'j', 'k', 'l', ';', '+', '*', '*Nil*'],
    ['*Nil*', '*Nil*', 'h', 'g', 'f', 'd', 's', 'a', '*cap*'],
    ['*Nil*', 'n', '*spc*', 'm', ',', '.', '/', '|', '*Nil*'],
    ['*SFT*', '*Nil*', '*Nil*', 'b', 'v', 'c', 'x', 'z', '*Nil*'],
]


def matrix_finder(n1, n2):
    n1 = CONVERTER_1[n1]
    n2 = CONVERTER_2[n2]

    n1 = n1 - 9
    n2 = n2 - 1

    return MATRIX[n2][n1]


def plot():
    wire_colors = [
        '#130A0F',
        '#8A5049',
        '#D70343',
        '#E07F54',
        '#EDE35A',
        '#00A462',
        '#1266B8',
        '#7F32A6',
    ]

    for wire_no in range(8):
        plt.step(
            wires[wire_no]['time'],
            wires[wire_no]['val'] + (8 - wire_no) * 3,
            color=wire_colors[wire_no]
        )
        plt.axhline((8 - wire_no) * 3 + 2, color='k', linestyle='--')

    def on_key_press(event):
        if event.key == 'm':
            n1, n2 = demultiplex(event.xdata)
            print(f'Time: {event.xdata}, key: {matrix_finder(n1, n2)}')

    cid = plt.figure(1).canvas.mpl_connect('key_press_event', on_key_press)

    plt.show()


def decode():
    first = iter(wires[6])
    second = iter(wires[6])
    next(second)

    do_read = True

    for f, s in zip(first, second):
        length = s['time'] - f['time']

        if s['val']:  # on
            # length of key press impulse == 0.0000642538
            if 0.00004 < length < 0.00008 and do_read:
                n1, n2 = demultiplex(f['time'] + length / 2)
                print(matrix_finder(n1, n2), end='')
                do_read = False

        else:  # off
            if length > 0.02:  # Waited long enough, next key
                do_read = True
    print()


def main():
    global wires
    converter()  # Run once, imports csv
    wires = np.load('data.npy')
    plot()  # Plot the data
    decode()  # Print flag


if __name__ == '__main__':
    main()
