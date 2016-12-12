from selectlib.filter import search
from selectlib.reader import Lines


def test_filter():
    lines = Lines([
        "one",
        "two",
        "three",
    ])
    term = "t"
    assert list(search(lines, term)) == [
        (1, [(0, 1)]),
        (2, [(0, 1)]),
    ]


def test_re():
    lines = Lines([
        "one",
        "some].*chars",
        "three",
    ])
    term = "].*"
    assert list(search(lines, term)) == [
        (1, [(4, 7)]),
    ]


def test_ignores_case():
    lines = Lines([
        "hone",
        "tHree",
    ])
    term = "h"
    assert list(search(lines, term)) == [
        (0, [(0, 1)]),
        (1, [(1, 2)]),
    ]


def test_uses_case():
    lines = Lines([
        "hone",
        "tHree",
    ])
    term = "H"
    assert list(search(lines, term)) == [
        (1, [(1, 2)]),
    ]


def test_multiple_terms():
    lines = Lines([
        "one of them",
        "two",
    ])
    term = "ne th"
    assert list(search(lines, term)) == [
        (0, [(1, 3), (7, 9)]),
    ]


def test_repeat():
    lines = Lines([
        "aaa",
    ])
    term = "aa"
    assert list(search(lines, term)) == [
        (0, [(0, 2)]),
    ]


def test_incorrect_mark_bug():
    lines = Lines([
        "/tests/test",
    ])
    term = "/test"
    assert list(search(lines, term)) == [
        (0, [(0, 5), (6, 11)]),
    ]
