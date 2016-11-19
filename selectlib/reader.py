def read(stream):
    return unique(stream.read().splitlines())


def unique(items):
    result = []
    seen = {}
    for item in items:
        if item not in seen:
            seen[item] = True
            result.append(item)
    return result
