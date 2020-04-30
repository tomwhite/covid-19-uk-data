import dateparser
import glob
import math
from parsers import get_text_from_html, parse_daily_areas, parse_daily_areas_pdf, parse_totals, parse_totals_pdf
import pdfplumber
import re
from util import lookup_local_authority_code, lookup_health_board_code, lookup_local_government_district_code, normalize_int, normalize_whitespace

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

def test_lookup_local_government_district_code():
    assert lookup_local_government_district_code("Antrim and Newtownabbey") == "N09000001"
    assert lookup_local_government_district_code("Bogus") == ""

def test_get_text_from_html():
    html = "<b>Some bold  text</b>"
    assert get_text_from_html("<b>Some bold  text<br/>new line</b>") == "Some bold text new line"

def test_parse_totals_scotland():
    for file in sorted(glob.glob("data/raw/coronavirus-covid-19-number-of-cases-in-scotland-*.html")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.html", file)
        date = m.group(1)
        if date <= "2020-03-18":
            # older pages cannot be parsed with current parser
            continue
        with open(file) as f:
            html = f.read()
            result = parse_totals("Scotland", html)
            print(date)
            assert result["Country"] == "Scotland"
            assert result["Date"] == date
            assert result["Tests"] >= 0
            assert result["ConfirmedCases"] >= 0
            assert result["Deaths"] >= 0

def test_parse_totals_wales():
    for file in sorted(glob.glob("data/raw/coronavirus-covid-19-number-of-cases-in-wales-*.html")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.html", file)
        date = m.group(1)
        if date <= "2020-03-17":
            # older pages cannot be parsed with current parser
            continue
        with open(file) as f:
            html = f.read()
            result = parse_totals("Wales", html)
            assert result["Country"] == "Wales"
            assert result["Date"] == date
            assert math.isnan(result["Tests"]) # Wales does not report test numbers
            assert result["ConfirmedCases"] >= 0
            assert result["Deaths"] >= 0

def test_parse_totals_uk():
    for file in sorted(glob.glob("data/raw/coronavirus-covid-19-number-of-cases-in-uk-*.html")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.html", file)
        date = m.group(1)
        if date <= "2020-03-22":
            # older pages cannot be parsed with current parser
            continue
        with open(file) as f:
            html = f.read()
            result = parse_totals("UK", html)
            assert result["Country"] == "UK"
            assert result["Date"] == date
            assert result["Tests"] >= 0
            assert result["ConfirmedCases"] >= 0
            assert result["Deaths"] >= 0

def test_parse_totals_pdf_ni():
    for file in sorted(glob.glob("data/raw/Daily_bulletin_DoH_*.pdf")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.pdf", file)
        date = m.group(1)
        if date <= "2020-03-24":
            # older pages cannot be parsed with current parser
            continue
        result = parse_totals_pdf(date, "Northern Ireland", file)
        assert result["Country"] == "Northern Ireland"
        assert result["Date"] == date
        assert result["Tests"] >= 0
        assert result["ConfirmedCases"] >= 0
        assert result["Deaths"] >= 0

def test_parse_totals_pdf_wales():
    for file in sorted(glob.glob("data/raw/phw/HeadlineSummary-*.pdf")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.pdf", file)
        date = m.group(1)
        result = parse_totals_pdf(date, "Wales", file)
        assert result["Country"] == "Wales"
        assert result["Date"] == date
        assert result["Tests"] >= 0
        assert result["ConfirmedCases"] >= 0
        if date < "2020-04-29":
            assert result["Deaths"] >= 0

def test_parse_daily_areas_scotland():
    for file in sorted(glob.glob("data/raw/coronavirus-covid-19-number-of-cases-in-scotland-*.html")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.html", file)
        date = m.group(1)
        if date <= "2020-03-18":
            # older pages cannot be parsed with current parser
            continue
        with open(file) as f:
            html = f.read()
            result = parse_daily_areas(date, "Scotland", html)
            assert len(result) > 1
            assert result[0] == ['Date', 'Country', 'AreaCode', 'Area', 'TotalCases']
            for row in result[1:]:
                assert row[0] == date
                assert row[1] == "Scotland"
                assert row[3] == "Golden Jubilee National Hospital" or len(row[2]) > 0
                assert len(row[3]) > 0
                assert row[3] == "Golden Jubilee National Hospital" or row[4] == "NaN" or int(row[4]) >= 0

def test_parse_daily_areas_wales():
    for file in sorted(glob.glob("data/raw/coronavirus-covid-19-number-of-cases-in-wales-*.html")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.html", file)
        date = m.group(1)
        if date <= "2020-03-18":
            # older pages cannot be parsed with current parser
            continue
        if date >= "2020-04-08":
            # daily areas no longer published on the HTML page
            continue
        with open(file) as f:
            html = f.read()
            result = parse_daily_areas(date, "Wales", html)
            assert len(result) > 1
            assert result[0] == ['Date', 'Country', 'AreaCode', 'Area', 'TotalCases']
            for row in result[1:]:
                assert row[0] == date
                assert row[1] == "Wales"
                assert row[2] is not None # Area code can be blank (e.g. 'To be confirmed')
                assert len(row[3]) > 0
                assert int(row[4]) >= 0

def test_parse_daily_areas_wales_pdf():
    for file in sorted(glob.glob("data/raw/phw/LAs-*.pdf")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.pdf", file)
        date = m.group(1)
        result = parse_daily_areas_pdf(date, "Wales", file)
        assert len(result) > 1
        assert result[0] == ['Date', 'Country', 'AreaCode', 'Area', 'TotalCases']
        for row in result[1:]:
            assert row[0] == date
            assert row[1] == "Wales"
            assert row[2] is not None # Area code can be blank (e.g. 'To be confirmed')
            assert len(row[3]) > 0
            assert int(row[4]) >= 0

def test_parse_daily_areas_ni():
    for file in sorted(glob.glob("data/raw/Daily_bulletin_DoH_*.pdf")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.pdf", file)
        date = m.group(1)
        if date <= "2020-03-25":
            # older pages don't have case numbers
            continue
        result = parse_daily_areas_pdf(date, "Northern Ireland", file)
        if result is None:
            # usually (but not always) because weekends don't have case numbers
            continue
        assert len(result) > 1
        assert result[0] == ['Date', 'Country', 'AreaCode', 'Area', 'TotalCases']
        for row in result[1:]:
            assert row[0] == date
            assert row[1] == "Northern Ireland"
            assert row[2] is not None # Area code can be blank (e.g. 'Unknown')
            assert len(row[3]) > 0
            assert int(row[4]) >= 0
