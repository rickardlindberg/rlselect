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


from ConfigParser import RawConfigParser


class Config(object):

    def __init__(self, path=None):
        self._config_parser = RawConfigParser()
        self._config_parser.add_section("theme")
        self._config_parser.set("theme", "highlight_fg", "RED")
        self._config_parser.set("theme", "highlight_bg", "BACKGROUND")
        self._config_parser.set("theme", "selection_fg", "WHITE")
        self._config_parser.set("theme", "selection_bg", "GREEN")
        self._config_parser.set("theme", "gui_font_size", "11")
        self._config_parser.set("theme", "gui_size", "900, 648")
        self._config_parser.add_section("rgb")
        self._config_parser.set("rgb", "BACKGROUND", "253, 246, 227")
        self._config_parser.set("rgb", "FOREGROUND", "101, 123, 131")
        self._config_parser.set("rgb", "BLACK", "7, 54, 66")
        self._config_parser.set("rgb", "BLUE", "38, 139, 210")
        self._config_parser.set("rgb", "CYAN", "42, 161, 152")
        self._config_parser.set("rgb", "GREEN", "133, 153, 0")
        self._config_parser.set("rgb", "MAGENTA", "211, 54, 130")
        self._config_parser.set("rgb", "RED", "220, 50, 47")
        self._config_parser.set("rgb", "WHITE", "238, 232, 213")
        self._config_parser.set("rgb", "YELLOW", "181, 137, 0")
        if path is not None:
            self._config_parser.read([path])

    def get_highlight_fg(self):
        return self._config_parser.get("theme", "highlight_fg")

    def get_highlight_bg(self):
        return self._config_parser.get("theme", "highlight_bg")

    def get_selection_fg(self):
        return self._config_parser.get("theme", "selection_fg")

    def get_selection_bg(self):
        return self._config_parser.get("theme", "selection_bg")

    def get_rgb(self, name):
        return self._get_int_tuple("rgb", name, 3)

    def get_gui_font_size(self):
        return self._config_parser.getint("theme", "gui_font_size")

    def get_gui_size(self):
        return self._get_int_tuple("theme", "gui_size", 2)

    def _get_int_tuple(self, section, name, size):
        result = tuple(
            int(x.strip())
            for x
            in self._config_parser.get(section, name).split(",")
        )
        if len(result) != size:
            raise ValueError("Expected {} integers but got {} for {}".format(
                size,
                len(result),
                name
            ))
        return result
