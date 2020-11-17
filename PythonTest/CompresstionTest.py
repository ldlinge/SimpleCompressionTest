#!/usr/bin/env python
""" Python test that calls C function through ctypes module. """
import ctypes
import numpy as np
import random

global tests_num
tests_num = 1000
global tests_total
tests_total = 0
global tests_passed
tests_passed = 0
global tests_failed
tests_failed = 0
global failed_list
failed_list = []

# load the shared library into c types.
libname = "../Debug/SimpleConcompressionC.dll"
LIBC = ctypes.CDLL(libname)

print("=" * 20)
LIBC.simple_compress.argtypes = ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int
LIBC.simple_compress.restype = ctypes.c_int

def gen_test_data(num_bytes=0, min_num=0, max_num=127, repeat=0):
    remaining_bytes = num_bytes
    data_array = []
    compressed_data = []
    repeat_override = 0
    prev_num = -1
    if repeat > 0:
        repeat_override = 1
        if repeat > num_bytes:
            repeat = num_bytes
    while remaining_bytes > 0:
        if min_num >= max_num:
            num = max_num
        else:
            num = random.randint(min_num, max_num)
            while prev_num == num and min_num < max_num:
                print(num)
                # if the new random num is the same as the previous it will complicate the repeat calculation so regenerate
                num = random.randint(min_num, max_num)
        if not repeat_override:
            repeat = random.randint(1, remaining_bytes)
        nums = np.repeat(num, repeat)
        if repeat > 1:
            compressed_data.append((repeat + 128) & 0xff) # make it an unsigned char
        compressed_data.append(num)
        data_array = [*data_array, *nums]
        remaining_bytes -= repeat
        prev_num = num

    return data_array, compressed_data

def decompress(list):
    marker = marker_prev = 0
    decompressed = []
    repeat = 1
    for i, element in enumerate(list):
        marker = element & 1 << 7
        if not marker_prev and marker:
            # marker set
            repeat = (element - 128) & 0xff
        elif marker_prev or not marker:
            marker = 0
            num = element & 0x7f
            nums = np.repeat(num, repeat)
            decompressed = [*decompressed, *nums]
            repeat = 1
        marker_prev = marker

    return decompressed


def gen_run_tests(num_tests, min_num_bytes=1, num_bytes=127, min_num=0, max_num=127, repeat=0, testcase="default"):
    global tests_num
    global tests_passed
    global tests_failed
    global failed_list

    print(testcase)

    for i in range(num_tests):
        testpass = 1
        if min_num_bytes >= num_bytes:
            numbytes = num_bytes
        else:
            numbytes=random.randint(min_num_bytes, num_bytes)
        data, comp = gen_test_data(num_bytes=numbytes, min_num=min_num, max_num=max_num, repeat=repeat)
        test = data.copy()
        print("-" * 20)

        testType = ctypes.c_ubyte * len(test)
        test_char = testType(*test)
        print([hex(x) for x in test_char])

        new_len = LIBC.simple_compress(test_char, len(test_char))
        if new_len == len(comp):
            print("PASS: expeced lengths match %d == %d" % (new_len, len(comp)))
        else:
            print("FAIL: expeced lengths don't match %d != %d" % (new_len, len(comp)))
            testpass = 0
        new_bits = test_char[:new_len]
        print(list([hex(x) for x in new_bits]))
        print([hex(x) for x in comp])
        if list(new_bits) == comp:
            print("PASS: outputs match")
            decompressed = decompress(list(new_bits))
            print([hex(x) for x in decompressed])
            print([hex(x) for x in data])
            if len(decompressed) == len(data):
                print("PASS: expeced lengths of decompressed match %d == %d" % (len(decompressed), len(data)))
            else:
                print("FAIL: expeced lengths don't match %d != %d" % (len(decompressed), len(data)))
                testpass = 0
            if decompressed == data:
                print("PASS: decompressed data matches original")  
            else:
                print("FAIL: decompressed data doesn't matches original")
                testpass = 0
        else:
            print("FAIL: outputs don't match")
            testpass = 0
        if testpass:
            tests_passed += 1
            print("TEST PASSED")
        else:
            tests_failed += 1
            failed_list.append( (testcase, len(test), [hex(x) for x in data], [hex(x) for x in decompressed], list([hex(x) for x in new_bits]), [hex(x) for x in comp]) )
            print("TEST FAILED")
            

if __name__ == "__main__":
    print("=" * 20)

    gen_run_tests(tests_num, num_bytes = 127, max_num = 127, testcase = "Random generated test data with max 127 bytes and max 127 (7bit)")
    tests_total += tests_num

    gen_run_tests(1, min_num_bytes=127, num_bytes = 0, max_num = 127, testcase = "0 size data")
    tests_total += 1

    # might fail
    gen_run_tests(4, num_bytes = 255, max_num = 127, testcase = "data greater than 127 bytes")
    tests_total += 4

    # will fail
    tests_to_run = 4
    gen_run_tests(tests_to_run, num_bytes = 127, min_num = 196, max_num = 255, testcase = "nums greater than 127")
    tests_total += tests_to_run

    gen_run_tests(1, num_bytes = 127, max_num = 0, repeat = 127, testcase = "0 repeated 127 times")
    tests_total += 1

    gen_run_tests(1, min_num_bytes=127, num_bytes = 127, min_num = 127, max_num = 127, repeat = 127, testcase = "127 repeated 127 times")
    tests_total += 1

    gen_run_tests(1, min_num_bytes=255, num_bytes = 255, repeat = 255, testcase = "data with repeating 255 times")
    tests_total += 1
    
    gen_run_tests(1, min_num_bytes=128, num_bytes = 128, repeat = 128, testcase = "data with repeating 128 times")
    tests_total += 1
    
    gen_run_tests(1, min_num_bytes=255, num_bytes=255, min_num=255, max_num=255, repeat=255, testcase="data with 255 repeating 255 times")
    tests_total += 1

    print("*" * 20)
    print("*" * 20)

    if (tests_passed == tests_total) and (tests_failed == 0):
        print("Success! All tests passed.")
    else:
        print("Fail! Not all tests passed.")
        print(failed_list)
    print("Tests run: %d, Tests passed: %d, Tests failed: %d" % (tests_total, tests_passed, tests_failed))

