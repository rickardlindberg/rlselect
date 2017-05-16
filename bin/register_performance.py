#!/usr/bin/env python
#
# Copyright (C) 2017  Rickard Lindberg
#
# This file is part of rlselect.
#
# rlselect is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rlselect is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rlselect.  If not, see <http://www.gnu.org/licenses/>.


import itertools
import StringIO
import sys
import timeit

from rlselectlib.filter import search
from rlselectlib.reader import read


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
