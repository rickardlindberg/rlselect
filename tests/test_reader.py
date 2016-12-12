from StringIO import StringIO

from selectlib.reader import read


def test_read():
    assert extract(read(StringIO("one\ntwo\r\nthree\rfour\n"))) == [
        "one",
        "two",
        "three",
        "four",
    ]


def test_read_skips_duplicates():
    assert extract(read(StringIO("dup\ndup"))) == [
        "dup",
    ]


def extract(lines):
    return [
        lines.raw(index)
        for index
        in range(lines.count())
    ]
