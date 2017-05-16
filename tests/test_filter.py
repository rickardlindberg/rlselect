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


from rlselectlib.filter import search
from rlselectlib.reader import Lines


def test_filter():
    lines = Lines([
        "one",
        "two",
        "three",
    ])
    term = "t"
    assert list(search(lines, term)) == [
        (1, [(0, 1)]),
        (2, [(0, 1)]),
    ]


def test_re():
    lines = Lines([
        "one",
        "some].*chars",
        "three",
    ])
    term = "].*"
    assert list(search(lines, term)) == [
        (1, [(4, 7)]),
    ]


def test_ignores_case():
    lines = Lines([
        "hone",
        "tHree",
    ])
    term = "h"
    assert list(search(lines, term)) == [
        (0, [(0, 1)]),
        (1, [(1, 2)]),
    ]


def test_uses_case():
    lines = Lines([
        "hone",
        "tHree",
    ])
    term = "H"
    assert list(search(lines, term)) == [
        (1, [(1, 2)]),
    ]


def test_multiple_terms():
    lines = Lines([
        "one of them",
        "two",
    ])
    term = "ne th"
    assert list(search(lines, term)) == [
        (0, [(1, 3), (7, 9)]),
    ]


def test_repeat():
    lines = Lines([
        "aaa",
    ])
    term = "aa"
    assert list(search(lines, term)) == [
        (0, [(0, 2)]),
    ]


def test_incorrect_mark_bug():
    lines = Lines([
        "/tests/test",
    ])
    term = "/test"
    assert list(search(lines, term)) == [
        (0, [(0, 5), (6, 11)]),
    ]
