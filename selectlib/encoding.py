import locale


def to_unicode(binary, fail=False):
    if fail:
        return binary.decode(locale.getpreferredencoding())
    else:
        return binary.decode(locale.getpreferredencoding(), "replace")


def to_binary(text):
    return text.encode(locale.getpreferredencoding())
