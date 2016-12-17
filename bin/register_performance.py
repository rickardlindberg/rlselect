#!/usr/bin/env python

import itertools
import StringIO
import sys
import timeit

from selectlib.filter import search
from selectlib.reader import read


NUMBER_OF_MEASUREMENTS = 10
NUMBER_OF_SAMPLE_POINTS = 10


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: {0} filename.dat".format(sys.argv[0]))
    else:
        with open(sys.argv[1], "w") as f:
            for values in time():
                f.write("\t".join(map(str, values)))
                f.write("\n")


def time():
    return time_variable(time_search_with_no_matches, 10000, 100000)


def time_variable(time_fn, start, stop):
    step = (stop - start) / NUMBER_OF_SAMPLE_POINTS
    for variable in range(start, stop, step):
        yield (variable, time_fn(variable))


def time_search_with_no_matches(number_of_lines):
    return time_search(
        number_of_lines=number_of_lines,
        line_fn=lambda index: "this is line number {0}".format(index),
        term="hello",
        max_results=10
    )


def time_search(number_of_lines, line_fn, term, max_results):
    results = []
    for _ in range(NUMBER_OF_MEASUREMENTS):
        stdin = StringIO.StringIO("\n".join([
            line_fn(index)
            for index
            in range(number_of_lines)
        ]))
        t1 = timeit.default_timer()
        list(itertools.islice(search(read(stdin), term), max_results))
        t2 = timeit.default_timer()
        results.append(t2 - t1)
    return min(results)


if __name__ == "__main__":
    main()
