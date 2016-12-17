from selectlib.encoding import to_unicode, to_binary


def read(stream):
    return Lines(unique(to_unicode(stream.read()).splitlines()))


def unique(items):
    result = []
    seen = {}
    for item in items:
        if item not in seen:
            seen[item] = True
            result.append(item)
    return result


class Lines(object):

    def __init__(self, lines):
        self._lines = lines

    def count(self):
        return len(self._lines)

    def raw(self, index):
        return to_binary(self._lines[index])

    def unicode(self, index):
        return self._lines[index]
