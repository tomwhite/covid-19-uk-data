#!/usr/bin/env python

# Extract local authority case data (Wales) from an HTML page and save in CSV format.

from bs4 import BeautifulSoup
import csv
import dateparser
import pandas as pd
import re
import sys

html_file = sys.argv[1]
csv_file = sys.argv[2]


def normalize_whitespace(text):
    s =  text.replace(
        u"\xa0", u" "
    ).replace(r"\S+", " ") # replace non-breaking spaces with regular spaces
    return re.sub('\s+', ' ', s).strip()


hb_mapping = pd.read_csv("data/raw/Local_Health_Boards_April_2019_Names_and_Codes_in_Wales.csv")
hb_name_to_code = dict(zip(hb_mapping["LHB19NM"], hb_mapping["LHB19CD"]))
hb_name_to_code = {k.replace(" Teaching Health Board", "").replace(" University Health Board", ""): v for k, v in hb_name_to_code.items()}
hb_name_to_code["Cwm Taf"] = "W11000030"

country = "Wales"

html = open(html_file).read()
soup = BeautifulSoup(html, features="html.parser")
table = soup.find_all("table")[-1]

text = soup.get_text()
text = text.replace(u"\xa0", u" ")  # replace non-breaking spaces with regular spaces

pattern = re.compile(r"(?s)Updated: (?P<time>.+?),? \S+ (?P<date>\d+\s\w+\s\d{4})")
m = re.search(pattern, text)
groups = m.groupdict()
date = dateparser.parse(groups["date"]).strftime("%Y-%m-%d")

output_rows = [["Date", "Country", "AreaCode", "Area", "TotalCases"]]
for table_row in table.findAll("tr"):
    columns = [normalize_whitespace(col.text) for col in table_row.findAll("td")]
    if len(columns) == 0:
        continue
    if columns[0] == "Health Board" or columns[0] == "Wales":
        continue
    la = (
        columns[0]
        .replace("City and County of Swansea", "Swansea")
        .replace("City of Cardiff", "Cardiff")
        .replace("Newport City", "Newport")
        .replace("County Borough Council", "")
        .replace("County Council", "")
        .replace("Council", "")
        .strip()
    )
    cases = columns[2]
    output_row = [date, country, hb_name_to_code.get(la, ""), la, cases]
    output_rows.append(output_row)

with open(csv_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(output_rows)
