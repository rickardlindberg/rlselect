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


import StringIO

from rlselectlib.reader import Lines


def test_splits_stream_into_lines():
    assert get_lines("one\ntwo\r\nthree\rfour\n", "ascii") == [
        u"one",
        u"two",
        u"three",
        u"four",
    ]


def test_skips_duplicate_lines():
    assert get_lines("dup\ndup", "ascii") == [
        u"dup",
    ]


def test_converts_unknown_bytes_to_special_character():
    UNICODCE_UNKNOWN_CHAR = u"\uFFFD"
    assert get_lines("a\xFFb", "ascii") == [
        u"a{0}b".format(UNICODCE_UNKNOWN_CHAR),
    ]


def get_lines(binary, encoding):
    lines = Lines.from_stream(StringIO.StringIO(binary), encoding)
    return [
        lines.get(index)
        for index
        in range(lines.count())
    ]
