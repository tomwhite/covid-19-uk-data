#!/usr/bin/env python

# Consolidate all the daily indicator files into one big CSV file.

import os
import sys

dir = "data/daily/indicators"
csv_out_file = "data/covid-19-indicators-uk.csv"

header = "Date,Country,Indicator,Value"

with open(csv_out_file, "w") as out:
    out.write("{}\n".format(header))
    for file in sorted(os.listdir(dir)):
        if file.endswith(".csv"):
            print(os.path.join(dir, file))
            with open(os.path.join(dir, file)) as f:
                content = f.readlines()
                out.writelines(content)
