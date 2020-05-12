#!/usr/bin/env python

from bs4 import BeautifulSoup
import glob
import itertools
import pandas as pd
import re
import sys

from parsers import parse_totals, parse_tests

from util import normalize_int

# Use the historical HTML files to generate a CSV.
# Some pages cannot be handled by the parser so they are filled in manually.
def generate_csv():
    indicator_tuples = list(itertools.product(
        ["", "Pillar1", "Pillar2", "Pillar4"],
        ["TestsPerformed", "PeopleTested", "Positive"],
        ["Daily", "Total"],
    ))
    indicators = ["{}{}{}".format(t[2], t[0], t[1]) for t in indicator_tuples] + ["DailyPillar2InPersonRoutes", "DailyPillar2DeliveryRoutes", "TotalPillar2InPersonRoutes", "TotalPillar2DeliveryRoutes"]
    columns = ["Date", "Country"] + indicators
    print(",".join(columns))
    for file in sorted(glob.glob("data/raw/coronavirus-covid-19-number-of-cases-in-uk-*.html")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.html", file)
        date = m.group(1)
        with open(file) as f:
            html = f.read()

        if date <= "2020-03-22":
            # older pages cannot be parsed with current parser
            continue

        # if date != "2020-04-28":
        #     continue

        if date <= "2020-04-07":
            totals_result = parse_totals("UK", html)
            result = { "TotalPeopleTested": totals_result["Tests"] }        
        else:
            result = parse_tests("UK", html)

        indicator_values = [result.get(indicator, "") for indicator in indicators]
        output_row = [date, "UK"] + indicator_values
        print(",".join([str(val) for val in output_row]))


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)

    generate_csv()
