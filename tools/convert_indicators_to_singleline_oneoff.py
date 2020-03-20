#!/usr/bin/env python

# Convert indicators file to single line files

import pandas as pd
import re

from util import camel_to_hyphens, format_country


def write_indicator_file(date, country, indicator, value):
    with open(
        "data/daily/indicators/covid-19-{}-{}-{}.csv".format(
            date, format_country(country), camel_to_hyphens(indicator)
        ),
        "w",
    ) as f:
        f.write("{},{},{},{}\n".format(date, country, indicator, value))


indicators = pd.read_csv("data/covid-19-indicators-uk.csv")
indicators_dict = indicators.to_dict("records")

for d in indicators_dict:
    write_indicator_file(d["Date"], d["Country"], d["Indicator"], d["Value"])
