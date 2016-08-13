# -*- coding: utf-8 -*-


def check5(inputs):
    print "Received input is : ", inputs
    return inputs

for i in range(50):
    print i
    if i % 5 == 0:
        inputs = raw_input("Enter your input: ")
        print "Please input 5:"
        inputs = check5(inputs)
        while (int(inputs) or 1) % 5 != 0:
            print inputs, type(inputs)
            inputs = raw_input("Re Enter your input: ")
            print "Please Re input 5:"
            inputs = check5(inputs)
