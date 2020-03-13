#!/usr/bin/env python

# Convert local authority case data (Wales) from daily cases counts (manually entered CSV) to a common CSV format.

import pandas as pd
import re
import sys

csv_in_file = "data/raw/wales-new-cases.csv"
csv_out_file = sys.argv[1]

m = re.match(".+(\d{4}-\d{2}-\d{2})-wales\.csv", csv_out_file)
date = m.group(1)

new_cases = pd.read_csv(csv_in_file)

la_mapping = pd.read_csv(
    "data/raw/Lower_Tier_Local_Authority_to_Upper_Tier_Local_Authority_April_2019_Lookup_in_England_and_Wales.csv"
)
la_name_to_code = dict(zip(la_mapping["UTLA19NM"], la_mapping["UTLA19CD"]))
la_name_to_code["Cornwall and Isles of Scilly"] = la_name_to_code["Cornwall"]
la_name_to_code["Hackney and City of London"] = la_name_to_code["Hackney"]

# Find total (cumulative) cases for each LA in the data.
# (Note that some LAs don't have new cases every day)
new_cases["TotalCases"] = new_cases.groupby("Area")["NewCases"].transform(
    pd.Series.cumsum
)

# Filter to date of interest
new_cases_filtered = new_cases[new_cases["Date"] <= date].groupby("Area").tail(1)

# Create a row for every Welsh area
welsh_las = pd.DataFrame(
    [
        ["Blaenau Gwent"],
        ["Bridgend"],
        ["Caerphilly"],
        ["Cardiff"],
        ["Carmarthenshire"],
        ["Ceredigion"],
        ["Conwy"],
        ["Denbighshire"],
        ["Flintshire"],
        ["Gwynedd"],
        ["Isle of Anglesey"],
        ["Merthyr Tydfil"],
        ["Monmouthshire"],
        ["Neath Port Talbot"],
        ["Newport"],
        ["Pembrokeshire"],
        ["Powys"],
        ["Rhondda Cynon Taf"],
        ["Swansea"],
        ["Torfaen"],
        ["Vale of Glamorgan"],
        ["Wrexham"],
    ],
    columns=["Area"],
)

total_cases = pd.merge(welsh_las, new_cases_filtered, how="left", on="Area")
total_cases = total_cases.fillna(0)
total_cases = total_cases.astype({"TotalCases": "int64"})
total_cases["Date"] = date
total_cases["Country"] = "Wales"
total_cases["AreaCode"] = total_cases.apply(
    lambda x: la_name_to_code.get(x["Area"], ""), axis=1
)
total_cases = total_cases[["Date", "Country", "AreaCode", "Area", "TotalCases"]]

total_cases.to_csv(csv_out_file, index=False)
