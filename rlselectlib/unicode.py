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


CTRL_W = u"\u0017"
CTRL_N = u"\u000E"
CTRL_P = u"\u0010"
CTRL_C = u"\u0003"
CTRL_G = u"\u0007"
ESC = u"\u001B"
BS = u"\u0008"
CR = u"\u000D"
LF = u"\u000A"
TAB = u"\u0009"


def is_printable(unicode_character):
    return ord(unicode_character) >= 32
