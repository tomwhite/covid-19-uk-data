#!/usr/bin/env python

# Extract local authority case data (England) or health board data (Scotland) from an HTML page and save in CSV format.

from bs4 import BeautifulSoup
import csv
import re
import sys

from util import normalize_whitespace, lookup_health_board_code

html_file = sys.argv[1]
csv_file = sys.argv[2]

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
    area_code = lookup_health_board_code(area)
    cases = columns[1]
    output_row = [date, country, area_code, area, cases]
    output_rows.append(output_row)

with open(csv_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(output_rows)
