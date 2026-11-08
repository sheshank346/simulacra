from verify import verify_quote

PAGE = "The app is only in English, my staff can't use it."


def test_exact_quote():
    assert verify_quote("only in English", PAGE)


def test_ignores_case_and_spacing():
    assert verify_quote("ONLY   in english", PAGE)


def test_curly_apostrophe():
    assert verify_quote("my staff can\u2019t use it", PAGE)


def test_wrong_quote_fails():
    assert not verify_quote("only in Kannada", PAGE)


def test_empty_quote_fails():
    assert not verify_quote("", PAGE)