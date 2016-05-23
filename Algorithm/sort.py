# -*- coding: utf-8 -*-
import time


def bubble_sort(num):
    for i in range(len(num)):
        for j in range(i, len(num)):
            if num[j] < num[i]:
                tmp = num[j]
                num[j] = num[i]
                num[i] = tmp
    return num


def selection_seq(num):
    for i in range(len(num)):
        position = i
        for j in range(i, len(num)):
            if num[position] > num[j]:
                position = j
            if position != i:
                tmp = num[position]
                num[position] = num[i]
                num[i] = tmp
    return num


def insertion_sort(num):
    if len(num) > 1:
        for i in range(1, len(num)):
            while i > 0 and num[i] > num[i-1]:
                tmp = num[i]
                num[i] = num[i-1]
                num[i-1] = tmp
                i -= 1
        return num


if __name__ == "__main__":
    seq = [22, 1, 33, 4, 7, 6, 8, 9, 11, 22, 56, 45, 23, 234, 24, 65, 78, 76, 809, 345, 34, 341, 567, 4567, 45674,
           47, 789, 879, 109, 78789, 787, 54,  4578,  4854, 5453, 879, 321, 62, 963, 248, 871, 365, 842, 347]
    print "-----------bubble_sort--------------"
    bubble_time = time.clock()
    print bubble_sort(seq), "\ntime = ", bubble_time - time.clock()
    print "--------selection_sort-------------"
    selection_time = time.clock()
    print selection_seq(seq), "\ntime = ", selection_time - time.clock()
    print "--------insertion_sort-------------"
    insertion_time = time.clock()
    print insertion_sort(seq), "\ntime = ", insertion_time - time.clock()
