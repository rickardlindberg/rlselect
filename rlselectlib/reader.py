class Lines(object):

    @staticmethod
    def from_stream(stream, encoding):
        return Lines(stream.read().decode(encoding, "replace").splitlines())

    def __init__(self, lines):
        self._lines = unique(lines)

    def iter(self):
        return enumerate(self._lines)

    def count(self):
        return len(self._lines)

    def get(self, index):
        return self._lines[index]


def unique(items):
    result = []
    seen = {}
    for item in items:
        if item not in seen:
            seen[item] = True
            result.append(item)
    return result
