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


class Lines(object):

    @staticmethod
    def from_stream(stream, encoding):
        return Lines(stream.read().decode(encoding, "replace").splitlines())

    def __init__(self, lines):
        self._lines = unique(lines)

    def iter(self):
        return enumerate(self._lines)

    def count(self):
        return len(self._lines)

    def get(self, index):
        return self._lines[index]


def unique(items):
    result = []
    seen = {}
    for item in items:
        if item not in seen:
            seen[item] = True
            result.append(item)
    return result
