import StringIO

from selectlib.reader import Lines


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
