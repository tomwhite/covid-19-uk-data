#!/usr/bin/env python

# Convert local authority case data (England) from CSV to a common CSV format, including a date column.

import pandas as pd
import re
import sys

csv_in_file = sys.argv[1]
csv_out_file = sys.argv[2]

m = re.match(".+(\d{4}-\d{2}-\d{2})\.csv", csv_in_file)
date = m.group(1)

df = pd.read_csv(csv_in_file)
df["Date"] = date
df["Country"] = "England"
df = df.rename(columns={"GSS_CD": "AreaCode", "GSS_NM": "Area"})
df = df[["Date", "Country", "AreaCode", "Area", "TotalCases"]]
df.to_csv(csv_out_file, index=False)
