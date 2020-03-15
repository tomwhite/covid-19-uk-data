#!/usr/bin/env python

# Extract daily totals from an HTML page and emit a CSV row (for appending to totals files)

from bs4 import BeautifulSoup
import dateparser
import math
import re
import sys

html_file = sys.argv[1]

html = open(html_file).read()
soup = BeautifulSoup(html, features="html.parser")

text = soup.get_text()
text = text.replace(u"\xa0", u" ")  # replace non-breaking spaces with regular spaces


def normalize_int(num):
    if isinstance(num, str):
        return int(num.replace(",", ""))
    return num


uk_pattern = re.compile(
    r"As of (?P<time>.+?) on (?P<date>.+?), (?P<tests>.+?) people have been tested in the UK, of which (?P<negative_tests>.+?) were confirmed negative and (?P<positive_tests>.+?) were confirmed as positive. (?P<deaths>.+?) patients who tested positive for COVID-19 have died."
)
wales_pattern = re.compile(
    r"(?s)Updated: (?P<time>.+?), \S+ (?P<date>\d+\s\w+\s\d{4}).+We can confirm that .+? new cases have tested positive.+in Wales, bringing the total number of confirmed cases to (?P<positive_tests>.+?)\."
)
scotland_pattern = re.compile(
    r"(?s)A total of (?P<tests>.+?) Scottish tests.+Of these:\s+(?P<negative_tests>.+?) tests were.+?negative\s+(?P<positive_tests>.+?) tests were.+?positive.+Last updated: (?P<time>.+?) on (?P<date>[^.]+)"
)
ni_pattern = re.compile(
    r"As of (?P<time>.+?) on (?P<date>.+?), testing has resulted in .+? new positive cases bringing the total number of cases in Northern Ireland to (?P<positive_tests>.+?)\."
)

patterns = [uk_pattern, wales_pattern, scotland_pattern, ni_pattern]

for pattern in patterns:
    m = re.search(pattern, text)
    if m is not None:
        groups = m.groupdict()
        date = dateparser.parse(groups["date"]).strftime("%Y-%m-%d")
        tests = normalize_int(groups.get("tests", float("nan")))

        tests = normalize_int(groups.get("tests", float('nan')))
        positive_tests = normalize_int(groups["positive_tests"])
        negative_tests = normalize_int(groups.get("negative_tests", float("nan")))
        deaths = groups.get("deaths", 0)  # TODO: parse #deaths for all countries
        print(
            "{},{},{},{}".format(
                date, "" if math.isnan(tests) else tests, positive_tests, deaths
            )
        )
        if tests != (positive_tests + negative_tests):
            sys.stderr.write("Total tests not equal to positive_tests + negative_tests\n")
            sys.exit(1)

        deaths = groups.get("deaths", 0) # TODO: parse #deaths for all countries

        sys.exit(0)

sys.stderr.write("Can't find case numbers. Perhaps the page format has changed?\n")
sys.exit(1)
