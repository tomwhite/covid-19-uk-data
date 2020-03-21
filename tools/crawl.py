#!/usr/bin/env python

from bs4 import BeautifulSoup
import dateparser
import math
import os
import re
import requests
import sys

from parsers import (
    parse_daily_areas,
    parse_totals,
    print_totals,
    scotland_pattern,
    save_indicators,
    save_daily_areas,
)
from util import format_country, normalize_int, normalize_whitespace

# takes a date
# download page (or use local one if exists)
# if dates don't match, then exit
# extracts totals, cases
# writes local files

# TODO: default to today if no date passed in
date = sys.argv[1]
country = sys.argv[2]

if country == "UK":
    html_url = "https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public"
elif country == "Scotland":
    html_url = "https://www.gov.scot/coronavirus-covid-19/"
elif country == "Wales":
    html_url = "https://phw.nhs.wales/news/public-health-wales-statement-on-novel-coronavirus-outbreak/"
elif country == "Northern Ireland":
    count = (dateparser.parse(date) - dateparser.parse("2020-03-08")).days
    html_url = "https://www.health-ni.gov.uk/news/latest-update-coronavirus-covid-19-{}".format(count)
local_html_file = "data/raw/coronavirus-covid-19-number-of-cases-in-{}-{}.html".format(
    format_country(country), date
)

save_html_file = False

try:
    with open(local_html_file) as f:
        html = f.read()
except FileNotFoundError:
    r = requests.get(html_url)
    html = r.text
    save_html_file = True

results = parse_totals(country, html)

if results is None:
    sys.stderr.write("Can't find numbers. Perhaps the page format has changed?\n")
    sys.exit(1)
elif results["Date"] != date:
    sys.stderr.write("Page is dated {}, but want {}\n".format(results["Date"], date))
    sys.exit(1)

daily_areas = parse_daily_areas(date, country, html)

print_totals(results)
#save_indicators(results)

if daily_areas is not None:
    save_daily_areas(date, country, daily_areas)

if save_html_file:
    with open(local_html_file, "w") as f:
        f.write(html)
