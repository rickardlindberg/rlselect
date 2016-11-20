def search(lines, expression):
    match = get_match_fn(expression)
    for index, line in enumerate(lines):
        result = match(line)
        if result is not None:
            yield (index, marks_to_ranges(result))


def get_match_fn(expression):
    def match(line):
        if ignore_case:
            line = line.lower()
        marks = set()
        for term, term_len in terms:
            index = line.find(term)
            if index == -1:
                # If one term doesn't match, the expression doesn't match.
                return None
            else:
                while index != -1:
                    marks.update(range(index, index+term_len+1))
                    index = line.find(term, index+term_len)
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
