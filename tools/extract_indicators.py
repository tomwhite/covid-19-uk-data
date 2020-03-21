#!/usr/bin/env python

import pandas as pd
import sys

from util import camel_to_hyphens, format_country

# Extract daily totals (indicators) from an XLSX file and save to a single-line file.

xslx_file = sys.argv[1]

df = pd.read_excel(xslx_file)
print(df)

d = df.to_dict("records")[0]

date = d["DateVal"].strftime("%Y-%m-%d")

print("{},{},{},{}".format(date, "UK", "ConfirmedCases", d["TotalUKCases"]))
print("{},{},{},{}".format(date, "UK", "Deaths", d["TotalUKDeaths"]))
print("{},{},{},{}".format(date, "England", "ConfirmedCases", d["EnglandCases"]))
print("{},{},{},{}".format(date, "Scotland", "ConfirmedCases", d["ScotlandCases"]))
print("{},{},{},{}".format(date, "Wales", "ConfirmedCases", d["WalesCases"]))
print("{},{},{},{}".format(date, "Northern Ireland", "ConfirmedCases", d["NICases"]))


def write_indicator_file(date, country, indicator, value):
    with open(
        "data/daily/indicators/covid-19-{}-{}-{}.csv".format(
            date, format_country(country), camel_to_hyphens(indicator)
        ),
        "w",
    ) as f:
        f.write("{},{},{},{}\n".format(date, country, indicator, value))


# write_indicator_file(date, "UK", "ConfirmedCases", "confirmed-cases", d["TotalUKCases"])
# write_indicator_file(date, "UK", "Deaths", "deaths", d["TotalUKDeaths"])
# write_indicator_file(
#     date, "England", "ConfirmedCases", "confirmed-cases", d["EnglandCases"]
# )
# write_indicator_file(
#     date, "Scotland", "ConfirmedCases", "confirmed-cases", d["ScotlandCases"]
# )
# write_indicator_file(
#     date, "Wales", "ConfirmedCases", "confirmed-cases", d["WalesCases"]
# )
# write_indicator_file(
#     date, "Northern Ireland", "ConfirmedCases", "confirmed-cases", d["NICases"]
# )
