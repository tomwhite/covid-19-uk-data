#!/usr/bin/env python

# Convert PHW XLSX file into CSVs

import pandas as pd
import requests

if __name__ == "__main__":
    # find latest URL from http://www2.nphs.wales.nhs.uk:8080/CommunitySurveillanceDocs.nsf
    url = "http://www2.nphs.wales.nhs.uk:8080/CommunitySurveillanceDocs.nsf/61c1e930f9121fd080256f2a004937ed/655e7005344c59c5802585b00047ad76/$FILE/Rapid%20COVID-19%20surveillance%20data.xlsx"
    local_file = "data/raw/phw/Rapid COVID-19 surveillance data.xlsx"

    r = requests.get(url)
    with open(local_file, "wb") as f:
        f.write(r.content)

    sheets = pd.read_excel(local_file, sheet_name=None)
    for sheet in sheets.keys():
        df = sheets[sheet]
        df.to_csv(f"data/raw/phw/csv/{sheet.replace(' ', '_')}.csv", index=False)
