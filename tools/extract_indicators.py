#!/usr/bin/env python

import pandas as pd
import sys

# Extract daily totals (indicators) from an XLSX file and print.

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
