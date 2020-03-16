#!/usr/bin/env python

import pandas as pd
import sys

# Extract daily totals (indictors) from an XLSX file and print. (Not yet used.)

xslx_file = sys.argv[1]

df = pd.read_excel(xslx_file)

print(df)