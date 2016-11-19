from selectlib.filter import search


def test_filter():
    lines = [
        "one",
        "two",
        "three",
    ]
    term = "t"
    assert list(search(lines, term)) == [
        (1, [(0, 1)]),
        (2, [(0, 1)]),
    ]


def test_re():
    lines = [
        "one",
        "some].*chars",
        "three",
    ]
    term = "].*"
    assert list(search(lines, term)) == [
        (1, [(4, 7)]),
    ]


def test_case():
    lines = [
        "one",
        "tHree",
    ]
    term = "h"
    assert list(search(lines, term)) == [
        (1, [(1, 2)]),
    ]


def test_multiple_terms():
    lines = [
        "one of them",
        "two",
    ]
    term = "ne th"
    assert list(search(lines, term)) == [
        (0, [(1, 3), (7, 9)]),
    ]
