#!/usr/bin/env python

# Consolidate all the daily area data into one big CSV file.

import os
import sys

dir = "data/daily"
csv_out_file = "data/covid-19-cases-uk.csv"

header = "Date,Country,AreaCode,Area,TotalCases"

with open(csv_out_file, "w") as out:
    out.write("{}\n".format(header))
    for file in sorted(os.listdir(dir)):
        if file.endswith(".csv"):
            print(os.path.join(dir, file))
            with open(os.path.join(dir, file)) as f:
                content = f.readlines()
                if content[0].strip() != header:
                    sys.stderr.write(
                        "{} invalid header: {}".format(
                            os.path.join(dir, file), content[0]
                        )
                    )
                    sys.exit(1)
                out.writelines(content[1:])
