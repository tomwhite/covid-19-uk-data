from parsers import get_text_from_html
from util import lookup_local_authority_code, lookup_health_board_code, normalize_int, normalize_whitespace

# Run these tests with `pytest tools/test.py`

def test_normalize_int():
    assert normalize_int("1") == 1
    assert normalize_int("1,001") == 1001
    assert normalize_int("seven") == 7

def test_normalize_whitespace():
    assert normalize_whitespace("  a  b ") == "a b"

def test_lookup_local_authority_code():
    assert lookup_local_authority_code("Powys") == "W06000023"
    assert lookup_local_authority_code("Bogus") == ""

def test_lookup_health_board_code():
    assert lookup_health_board_code("Fife") == "S08000029"
    assert lookup_health_board_code("Bogus") == ""

def test_get_text_from_html():
    html = "<b>Some bold  text</b>"
    assert get_text_from_html("<b>Some bold  text<br/>new line</b>") == "Some bold text new line"
