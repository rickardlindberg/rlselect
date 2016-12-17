def search(lines, expression):
    match = get_match_fn(expression)
    for index in xrange(lines.count()):
        result = match(lines.unicode(index))
        if result is not None:
            yield (index, marks_to_ranges(result))


def get_match_fn(expression):
    def match(line):
        if ignore_case:
            line = line.lower()
        marks = set()
        for term, term_len in terms:
            if term in line:
                index = line.find(term)
                while index != -1:
                    marks.update(range(index, index+term_len))
                    index = line.find(term, index+term_len)
            else:
                # If one term doesn't match, the expression doesn't match.
                return None
        return marks
    ignore_case = expression == expression.lower()
    terms = [(term, len(term)) for term in expression.split()]
    return match


def marks_to_ranges(marks):
    result = []
    start = None
    end = None
    for mark in sorted(marks):
        if start is None:
            start = mark
            end = start + 1
        elif mark > end:
            result.append((start, end))
            start = mark
            end = start + 1
        else:
            end = mark + 1
    if start is not None:
        result.append((start, end))
    return result
