import re


def clean(text):
    text = text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", text).lower().strip()


def verify_quote(quote, page_text):
    q = clean(quote)
    return bool(q) and q in clean(page_text)