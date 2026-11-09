from verify import contains, verify_quote

PAGE = "The app is only in English, my staff can't use it."


def test_exact_quote():
    assert verify_quote("the app is only in English", PAGE)


def test_ignores_case_and_spacing():
    assert verify_quote("THE   APP is only in english", PAGE)


def test_curly_apostrophe():
    assert verify_quote("my staff can\u2019t use it", PAGE)


def test_wrong_quote_fails():
    assert not verify_quote("the app is only in Kannada", PAGE)


def test_empty_quote_fails():
    assert not verify_quote("", PAGE)


def test_punctuation_only_quote_fails():
    assert not verify_quote("...", PAGE)


def test_markdown_formatting_ignored():
    page = "AI receipt itemization\n:   Upload a photo of your receipt."
    assert verify_quote("AI receipt itemization: Upload a photo of your receipt", page)


def test_partial_word_does_not_match():
    assert not contains("glish", PAGE)


def test_short_fragment_fails():
    assert not verify_quote("only in English", PAGE)


def test_contains_allows_short_names():
    assert contains("English", PAGE)