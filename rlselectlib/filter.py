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


def search(lines, expression):
    match = get_match_fn(expression)
    for index, line in lines.iter():
        result = match(line)
        if result is not None:
            yield (index, marks_to_ranges(result))


def get_match_fn(expression):
    def match(line):
        if ignore_case:
            line = line.lower()
        marks = set()
        for term, term_len in terms:
            if term in line:
                index = line.find(term)
                while index != -1:
                    marks.update(range(index, index+term_len))
                    index = line.find(term, index+term_len)
            else:
                # If one term doesn't match, the expression doesn't match.
                return None
        return marks
    ignore_case = expression == expression.lower()
    terms = [(term, len(term)) for term in expression.split()]
    return match


def marks_to_ranges(marks):
    result = []
    start = None
    end = None
    for mark in sorted(marks):
        if start is None:
            start = mark
            end = start + 1
        elif mark > end:
            result.append((start, end))
            start = mark
            end = start + 1
        else:
            end = mark + 1
    if start is not None:
        result.append((start, end))
    return result
