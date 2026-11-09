import re

MIN_WORDS = 6


def clean(text):
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def contains(needle, haystack):
    n = clean(needle)
    return bool(n) and f" {n} " in f" {clean(haystack)} "


def verify_quote(quote, page_text):
    return len(clean(quote).split()) >= MIN_WORDS and contains(quote, page_text)