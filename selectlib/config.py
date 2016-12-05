class Config(object):

    def get_highlight_fg(self):
        return "RED"

    def get_highlight_bg(self):
        return "BACKGROUND"

    def get_selection_fg(self):
        return "WHITE"

    def get_selection_bg(self):
        return "GREEN"

    def get_rgb(self, name):
        return {
            "BACKGROUND": (253, 246, 227),
            "FOREGROUND": (101, 123, 131),
            "BLACK": (7, 54, 66),
            "BLUE": (38, 139, 210),
            "CYAN": (42, 161, 152),
            "GREEN": (133, 153, 0),
            "MAGENTA": (211, 54, 130),
            "RED": (220, 50, 47),
            "WHITE": (238, 232, 213),
            "YELLOW": (181, 137, 0),
        }[name]

    def get_gui_font_size(self):
        return 11

    def get_gui_size(self):
        return (900, 648)
