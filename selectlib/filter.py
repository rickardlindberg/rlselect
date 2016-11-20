def search(lines, expression):
    match = get_match_fn(expression)
    for index, line in enumerate(lines):
        result = match(line)
        if result is not None:
            yield (index, marks_to_ranges(result))


def get_match_fn(expression):
    terms = [(x, len(x)) for x in expression.split()]
    def match(line):
        lower = line.lower()
        marks = set()
        for term, n in terms:
            index = lower.find(term)
            if index == -1:
                return None
            else:
                while index != -1:
                    for mark in range(index, index+n+1):
                        marks.add(mark)
                    index = lower.find(term, index+n)
        return marks
    return match


def marks_to_ranges(marks):
    result = []
    start = None
    end = None
    for mark in sorted(marks):
        if start is None:
            start = mark
            end = start
        elif mark > end+1:
            result.append((start, end))
            start = mark
            end = start
        else:
            end = mark
    if start is not None:
        result.append((start, end))
    return result
