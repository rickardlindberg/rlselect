import re


def search(lines, terms):
    term_res = [term_to_re(term) for term in terms.split()]
    for index, line in enumerate(lines):
        result = match(index, line, term_res)
        if result:
            yield result


def match(index, line, term_res):
    marks = set()
    for term_re in term_res:
        matches = list(term_re.finditer(line))
        if matches:
            for match in matches:
                for mark in range(match.start(), match.end()+1):
                    marks.add(mark)
        else:
            return None
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
    return (index, result)


def term_to_re(term):
    return re.compile("".join([
        "[{}]".format(char)
        for char in term
    ]), flags=re.IGNORECASE)
