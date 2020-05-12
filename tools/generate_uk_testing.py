#!/usr/bin/env python

from bs4 import BeautifulSoup
import glob
import pandas as pd
import re
import sys

from parsers import parse_totals, parse_tests

from util import normalize_int

# Use the historical HTML files to generate a CSV.
# Some pages cannot be handled by the parser so they are filled in manually.
def generate_csv():
    print("Date,Country,DailyTestsPerformed,TotalTestsPerformed,DailyPeopleTested,TotalPeopleTested,DailyPositive,TotalPositive")
    for file in sorted(glob.glob("data/raw/coronavirus-covid-19-number-of-cases-in-uk-*.html")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.html", file)
        date = m.group(1)
        with open(file) as f:
            html = f.read()

        if date <= "2020-03-22":
            # older pages cannot be parsed with current parser
            continue

        if date <= "2020-04-07":
            result = parse_totals("UK", html)
            print("{},UK,,,,{},,".format(date, result["Tests"]))
            continue

        result = parse_tests("UK", html)
        output_row = [date, "UK", result["DailyTestsPerformed"], result["TotalTestsPerformed"], result["DailyPeopleTested"], result["TotalPeopleTested"], result["DailyPositive"], result["TotalPositive"]]
        print(",".join([str(val) for val in output_row]))


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)

    generate_csv()
