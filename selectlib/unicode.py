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
