#!/usr/bin/env python

# Extract local authority case data (England) or health board data (Scotland) from an HTML page and save in CSV format.

from bs4 import BeautifulSoup
import csv
import pandas as pd
import re
import sys

html_file = sys.argv[1]
csv_file = sys.argv[2]


def normalize_whitespace(text):
    return text.replace(
        u"\xa0", u" "
    ).strip()  # replace non-breaking spaces with regular spaces


# Get upper tier local authority name to code mapping.
# Note that this does not include Scotland, but that's OK as Scotland areas are health boards, not local authorities.
la_mapping = pd.read_csv(
    "data/raw/Lower_Tier_Local_Authority_to_Upper_Tier_Local_Authority_April_2019_Lookup_in_England_and_Wales.csv"
)
la_name_to_code = dict(zip(la_mapping["UTLA19NM"], la_mapping["UTLA19CD"]))
la_name_to_code["Cornwall and Isles of Scilly"] = la_name_to_code["Cornwall"]
la_name_to_code["Hackney and City of London"] = la_name_to_code["Hackney"]

hb_mapping = pd.read_csv("data/raw/geography_codes_and_labels_hb2014_01042019.csv")
hb_mapping = hb_mapping[
    hb_mapping.HB2014QF != "x"
]  # drop those marked with an 'x' since they are no longer in use
hb_name_to_code = dict(zip(hb_mapping["HB2014Name"], hb_mapping["HB2014"]))
hb_name_to_code = {k.replace("NHS ", ""): v for k, v in hb_name_to_code.items()}

m = re.match(".+-(.+)-(\d{4}-\d{2}-\d{2})\.html", html_file)
country = m.group(1).title()
date = m.group(2)

html = open(html_file).read()
soup = BeautifulSoup(html, features="html.parser")
table = soup.find_all("table")[-1]

output_rows = [["Date", "Country", "AreaCode", "Area", "TotalCases"]]
for table_row in table.findAll("tr"):
    columns = [normalize_whitespace(col.text) for col in table_row.findAll("td")]
    if len(columns) == 0:
        continue
    area = columns[0].replace("Ayrshire & Arran", "Ayrshire and Arran")
    area_code = hb_name_to_code.get(area, la_name_to_code.get(area, ""))
    cases = columns[1]
    output_row = [date, country, area_code, area, cases]
    output_rows.append(output_row)

with open(csv_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(output_rows)
