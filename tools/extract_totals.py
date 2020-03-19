#!/usr/bin/env python

# Extract daily totals from an HTML page and emit a CSV row (for appending to totals files)

from bs4 import BeautifulSoup
import dateparser
import math
import re
import sys
from word2number import w2n

html_file = sys.argv[1]

html = open(html_file).read()
soup = BeautifulSoup(html, features="html.parser")

text = soup.get_text()
text = text.replace(u"\xa0", u" ")  # replace non-breaking spaces with regular spaces


def normalize_whitespace(text):
    return text.replace(
        u"\xa0", u" "
    ).strip()  # replace non-breaking spaces with regular spaces


def normalize_int(num):
    if isinstance(num, str):
        return w2n.word_to_num(num.replace(",", ""))
    return num


uk_pattern = re.compile(
    r"As of (?P<time>.+?) on (?P<date>.+?), (?P<tests>.+?) people have been tested in the (?P<country>.+?), of which (?P<negative_tests>.+?) were confirmed negative and (?P<positive_tests>.+?) were confirmed.+?positive."
)
wales_pattern = re.compile(
    r"(?s)Updated: (?P<time>.+?),? \S+ (?P<date>\d+\s\w+\s\d{4}).+? new cases have tested positive.+in (?P<country>.+?), bringing the total number of confirmed cases to (?P<positive_tests>\w+).+?(?P<deaths>.+?) people in Wales.+?have died"
)
scotland_pattern = re.compile(
    r"(?s)A total of (?P<tests>.+?) (?P<country>.+?) tests.+Of these:\s+(?P<negative_tests>.+?) tests were.+?negative\s+(?P<positive_tests>.+?) tests were.+?positive.+Sadly, (?P<deaths>.+?) patients? in Scotland who tested positive.+?have died.+Last updated: (?P<time>.+?) on (?P<date>[^.]+)"
)
ni_pattern = re.compile(
    r"As of (?P<time>.+?) on (?P<date>.+?), testing has resulted in .+? new positive cases bringing the total number of cases in (?P<country>.+?) to (?P<positive_tests>.+?)\."
)

patterns = [uk_pattern, wales_pattern, scotland_pattern, ni_pattern]

for pattern in patterns:
    m = re.search(pattern, text)
    if m is not None:
        groups = m.groupdict()
        date = dateparser.parse(groups["date"]).strftime("%Y-%m-%d")
        country = normalize_whitespace(groups.get("country")).replace(
            "Scottish", "Scotland"
        )
        tests = normalize_int(groups.get("tests", float("nan")))
        positive_tests = normalize_int(groups["positive_tests"])
        negative_tests = normalize_int(groups.get("negative_tests", float("nan")))
        deaths = normalize_int(groups.get("deaths", float("nan")))
        if not math.isnan(tests):
            print("{},{},{},{}".format(date, country, "Tests", tests))
        if not math.isnan(positive_tests):
            print("{},{},{},{}".format(date, country, "ConfirmedCases", positive_tests))
        if not math.isnan(deaths):
            print("{},{},{},{}".format(date, country, "Deaths", deaths))
        print(
            "{},{},{},{}".format(
                date,
                "" if math.isnan(tests) else tests,
                positive_tests,
                "" if math.isnan(deaths) else deaths,
            )
        )
        if all(
            [not math.isnan(t) for t in (tests, positive_tests, negative_tests)]
        ) and tests != (positive_tests + negative_tests):
            sys.stderr.write(
                "Total tests not equal to positive_tests + negative_tests\n"
            )
            sys.exit(1)
        sys.exit(0)

sys.stderr.write("Can't find case numbers. Perhaps the page format has changed?\n")
sys.exit(1)
