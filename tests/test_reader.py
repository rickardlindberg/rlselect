from StringIO import StringIO

from selectlib.reader import read


def test_read():
    assert read(StringIO("one\ntwo\r\nthree\rfour\n")) == [
        "one",
        "two",
        "three",
        "four",
    ]


def test_read_skips_duplicates():
    assert read(StringIO("dup\ndup")) == [
        "dup",
    ]
