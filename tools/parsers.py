from bs4 import BeautifulSoup
import csv
import dateparser
import math
import pdfplumber
import re
import sqlite3
from titlecase import titlecase

from util import (
    format_country,
    is_blank,
    normalize_int,
    normalize_whitespace,
    lookup_health_board_code,
    lookup_local_authority_code,
    lookup_local_government_district_code,
)

def get_text_from_html(html):
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text(separator=" ")
    text = normalize_whitespace(text)
    return text

def date_value_parser_fn(value):
    return dateparser.parse(value, locales=["en-GB"]).strftime("%Y-%m-%d")


def int_value_parser_fn(value):
    return normalize_int(value)


def nan_value_parser_fn(value):
    return float("nan")


def get_match(pattern, text, group_name):
    m = re.search(pattern, text)
    return m.group(group_name) if m else None


def parse_totals_general(pattern_dict, country, text):
    result = {
        "Country": country
    }
    for (name, (patterns, value_parser_fn)) in pattern_dict.items():
        if patterns is None:
            result[name] = value_parser_fn(None)
            continue
        if type(patterns) is not tuple:
            patterns = (patterns,)
        for pattern in patterns:
            value = get_match(pattern, text, name)
            if value is None:
                continue
            result[name] = value_parser_fn(value)
            break
        if not name in result:
            print("Could not parse '{}'".format(name))
            return None
    return result

def parse_totals(country, html):
    text = get_text_from_html(html)
    if country == "UK":
        pattern_dict = {
            "Date": (r"As of (?P<Time>\d+(am|pm)?) (on )?(?P<Date>.+?),", date_value_parser_fn),
            "Tests": (r"(a total of )?(?P<Tests>[\d,]+?) people have been tested", int_value_parser_fn),
            "ConfirmedCases": (r"(and|of which|of whom) (?P<ConfirmedCases>[\d,]+?) (were confirmed (as )?|(have )?tested )positive", int_value_parser_fn),
            "Deaths": (r"(?P<Deaths>[\d,]+) (patients?.+?)?have (sadly )?died", int_value_parser_fn),
        }
        result = parse_totals_general(pattern_dict, country, text)
        return result
    elif country == "Scotland":
        pattern_dict = {
            "Date": (r"Scottish (COVID-19 )?test numbers: (?P<Date>\d+\s\w+\s\d{4})", date_value_parser_fn),
            "Tests": (r"total of (?P<Tests>.+?) (Scottish tests have concluded|people in Scotland have been tested)", int_value_parser_fn),
            "ConfirmedCases": (r"(?P<ConfirmedCases>[\d,]+?) (tests )?were (confirmed)?positive", int_value_parser_fn),
            "Deaths": (r"(?P<Deaths>(\d+|\d+[\d,]+|\d+)) patients?.+?have died", int_value_parser_fn),
        }
        result = parse_totals_general(pattern_dict, country, text)
        return result
    elif country == "Wales":
        pattern_dict = {
            "Date": (r"Updated: (?P<Time>.+?),? \S+ (?P<Date>\d+\s\w+(\s\d{4})?)", date_value_parser_fn),
            "Tests": (None, nan_value_parser_fn),
            "ConfirmedCases": (r"total number of confirmed cases to (?P<ConfirmedCases>[\d]+[\d,]*[\d]*)", int_value_parser_fn),
            "Deaths": ((r"(?P<Deaths>\w+) people in Wales who tested positive.+? died", r"the number of deaths in Wales to (?P<Deaths>\w+)"), int_value_parser_fn),
        }
        result = parse_totals_general(pattern_dict, country, text)
        return result
    elif country == "Northern Ireland":
        pattern_dict = {
            "Date": (r"As of (?P<Time>.+?) on (?P<Date>.+?),", date_value_parser_fn),
            "Tests": (r"total number of tests completed in Northern Ireland is (?P<Tests>.+?)\.", int_value_parser_fn),
            "ConfirmedCases": (r"total number of confirmed cases in Northern Ireland to (?P<ConfirmedCases>.+?)\.", int_value_parser_fn),
            "Deaths": (r"To date (?P<Deaths>.+?) people who tested positive have sadly died\.", int_value_parser_fn),
        }
        result = parse_totals_general(pattern_dict, country, text)
        return result
    return None


def parse_tests(country, html):

    def is_testing_table(table):
        headers = [th.text for th in table.findAll("th")]
        return "Tests" in headers

    soup = BeautifulSoup(html, features="html.parser")
    tables = soup.find_all("table")
    testing_tables = [table for table in tables if is_testing_table(table)]
    if len(testing_tables) == 0:
        print("Testing table not found")
        return None
    elif len(testing_tables) > 1:
        print("More than one testing table found")
        return None
    testing_table = testing_tables[0]
    table_rows = testing_table.findAll("tr")
    if len(table_rows) != 3:
        print("Expecting 3 table rows")
        return None
    daily_row = [td.text for td in table_rows[1].findAll("td")]
    total_row = [td.text for td in table_rows[2].findAll("td")]

    text = get_text_from_html(html)
    pattern_dict = {
        "Date": (r"As of (?P<Time>\d+(am|pm)?) (on )?(?P<Date>.+?),", date_value_parser_fn)
    }
    result = parse_totals_general(pattern_dict, country, text)
    result["DailyTestsPerformed"] = normalize_int(daily_row[1])
    result["DailyPeopleTested"] = normalize_int(daily_row[2])
    result["DailyPositive"] = normalize_int(daily_row[3])
    result["TotalTestsPerformed"] = normalize_int(total_row[1])
    result["TotalPeopleTested"] = normalize_int(total_row[2])
    result["TotalPositive"] = normalize_int(total_row[3])
    return result


def get_text_from_pdf(local_pdf_file):
    pdf = pdfplumber.open(local_pdf_file)
    page = pdf.pages[0] # just extract first page
    text = page.extract_text()
    text = normalize_whitespace(text)
    return text


def parse_totals_pdf(date, country, local_pdf_file):
    if country == "Northern Ireland":
        text = get_text_from_pdf(local_pdf_file)
        pattern_dict = {
            "Date": (r"Date generated: (?P<Date>[\d,]+/[\d,]+/[\d,]+)", date_value_parser_fn),
            "Tests": (r"Number of Individuals tested( for COVID-19| for SARS-COV2 Virus)?:? (?P<Tests>[\d,]+)", int_value_parser_fn),
            "ConfirmedCases": (r"(Number of Individuals (with confirmed|testing positive for) (COVID-19|SARS-COV2 Virus)|Cumulative number of laboratory confirmed COVID-19 cases):? (?P<ConfirmedCases>[\d,]+)", int_value_parser_fn),
            "Deaths": (r"(Total|Cumulative) number of (Trust |reported )?deaths( associated with COVID-19)?: (?P<Deaths>[\d,]+)", int_value_parser_fn),
        }
        result = parse_totals_general(pattern_dict, country, text)
        return result
    elif country == "Wales":
        pdf = pdfplumber.open(local_pdf_file)
        for page in pdf.pages:
            try:
                table = page.extract_table(table_settings = {
                    # use text alignment since the table doesn't have lines
                    "horizontal_strategy": "text"
                })
                result = {
                    "Date": date,
                    "Country": country
                }
                for table_row in table:
                    if table_row[0] == "":
                        continue
                    label = table_row[0].replace("\t", " ")
                    value = normalize_int(table_row[1])
                    if label == "Cumulative individuals tested":
                        result["Tests"] = value
                    elif label == "Cumulative confirmed COVID-19 case total":
                        result["ConfirmedCases"] = value
                    elif label == "Cumulative number of suspected COVID-19 deaths* reported to PHW":
                        # Get deaths from XLSX after this date
                        if date < "2020-04-29":
                            result["Deaths"] = value
                return result
            except IndexError:
                pass # no table on page
    return None

def print_totals(results):
    date = results["Date"]
    country = results["Country"]
    tests = results["Tests"]
    confirmed_cases = results["ConfirmedCases"]
    deaths = results.get("Deaths", float("NaN"))
    if not math.isnan(tests):
        print("{},{},{},{}".format(date, country, "Tests", tests))
    if not math.isnan(confirmed_cases):
        print("{},{},{},{}".format(date, country, "ConfirmedCases", confirmed_cases))
    if not math.isnan(deaths):
        print("{},{},{},{}".format(date, country, "Deaths", deaths))
    print(
        "{},{},{},{}".format(
            date,
            "" if math.isnan(tests) else tests,
            confirmed_cases,
            "" if math.isnan(deaths) else deaths,
        )
    )


def save_indicators(results):
    date = results["Date"]
    country = results["Country"]
    tests = results["Tests"]
    confirmed_cases = results["ConfirmedCases"]
    deaths = results.get("Deaths", float("NaN"))
    if not math.isnan(tests):
        with open(
            "data/daily/indicators/covid-19-{}-{}-tests.csv".format(
                date, format_country(country)
            ),
            "w",
        ) as f:
            f.write("{},{},{},{}\n".format(date, country, "Tests", tests))
    if not math.isnan(confirmed_cases):
        with open(
            "data/daily/indicators/covid-19-{}-{}-confirmed-cases.csv".format(
                date, format_country(country)
            ),
            "w",
        ) as f:
            f.write(
                "{},{},{},{}\n".format(date, country, "ConfirmedCases", confirmed_cases)
            )
    if not math.isnan(deaths):
        with open(
            "data/daily/indicators/covid-19-{}-{}-deaths.csv".format(
                date, format_country(country)
            ),
            "w",
        ) as f:
            f.write("{},{},{},{}\n".format(date, country, "Deaths", deaths))


def save_indicators_to_sqlite(results):
    date = results["Date"]
    country = results["Country"]
    tests = results["Tests"]
    confirmed_cases = results["ConfirmedCases"]
    deaths = results.get("Deaths", float("NaN"))
    with sqlite3.connect('data/covid-19-uk.db') as conn:
        c = conn.cursor()
        if not math.isnan(tests):
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', '{country}', 'Tests', {tests})")
        if not math.isnan(confirmed_cases):
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', '{country}', 'ConfirmedCases', {confirmed_cases})")
        if not math.isnan(deaths):
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', '{country}', 'Deaths', {deaths})")


def parse_daily_areas(date, country, html):
    if country in ("Northern Ireland", "UK"):
        return None
    soup = BeautifulSoup(html, features="html.parser")
    output_rows = [["Date", "Country", "AreaCode", "Area", "TotalCases"]]
    if country == "Scotland":
        table = soup.find_all("table")[0]
        for table_row in table.findAll("tr"):
            columns = [
                normalize_whitespace(col.text) for col in table_row.findAll("td")
            ]
            if len(columns) == 0:
                continue
            if columns[0].lower() in ("", "health board"):
                continue
            area = columns[0].replace("Ayrshire & Arran", "Ayrshire and Arran")
            area = columns[0].replace("Eileanan Siar (Western Isles)", "Western Isles")
            area_code = lookup_health_board_code(area)
            cases = columns[1]
            if cases == "*": # means 5 or fewer cases
                cases = "NaN"
            else:
                cases = cases.replace("*", "").replace(",", "")
            output_row = [date, country, area_code, area, cases]
            output_rows.append(output_row)
        return output_rows
    elif country == "Wales":
        if date >= "2020-04-08":
            # daily areas no longer published on the HTML page (now published on the dashboard)
            return None
        table = soup.find_all("table")[0]
        for table_row in table.findAll("tr"):
            columns = [
                normalize_whitespace(col.text) for col in table_row.findAll("td")
            ]
            if len(columns) == 0:
                continue
            if columns[0].lower() in ("", "health board", "wales", "total", "wales total"):
                continue
            if is_blank(columns[-1]):
                continue
            area = (
                columns[0]
                .replace("City and County of Swansea", "Swansea")
                .replace("City of Cardiff", "Cardiff")
                .replace("Newport City", "Newport")
                .replace("County Borough Council", "")
                .replace("County Council", "")
                .replace("Council", "")
                .replace("Cardiff & Vale", "Cardiff and Vale")
                .replace("Cwm Taf Morgannwg", "Cwm Taf")
                .strip()
            )
            if is_blank(area):
                area = columns[0]
            cases = columns[-1].replace("*","").replace(",", "")
            output_row = [date, country, lookup_health_board_code(area), area, cases]
            output_rows.append(output_row)
        return output_rows
    return None


def parse_daily_areas_json(date, country, json_data):
    if country == "England":
        output_rows = [["Date", "Country", "AreaCode", "Area", "TotalCases"]]
        for area_code, o in json_data["utlas"].items():
            area = o["name"]["value"]
            cases = normalize_int(o["totalCases"]["value"])
            if area_code != lookup_local_authority_code(area):
                print("Area code mismatch for {}, JSON file gave {}, but lookup was {}".format(area, area_code, lookup_local_authority_code(area)))
                return None
            output_row = [date, country, area_code, area, cases]
            output_rows.append(output_row)
        return output_rows

    return None


def parse_daily_areas_pdf(date, country, local_pdf_file):
    if country == "Northern Ireland":
        pdf = pdfplumber.open(local_pdf_file)
        for page in pdf.pages:
            try:
                table = page.extract_table(table_settings = {
                    # use text alignment since the table doesn't have lines
                    "horizontal_strategy": "text"
                })
                if table[0][0] == "Local Government District":
                    output_rows = [["Date", "Country", "AreaCode", "Area", "TotalCases"]]
                    for table_row in table[1:]:
                        if table_row[0].lower() in ("", "total"):
                            continue
                        area = normalize_whitespace(titlecase(table_row[0]))
                        area = area.replace("Ards and North Down", "North Down and Ards")
                        area_code = lookup_local_government_district_code(area)
                        cases = normalize_int(table_row[1])
                        output_row = [date, country, area_code, area, cases]
                        output_rows.append(output_row)
                    return output_rows
            except IndexError:
                pass # no table on page
    elif country == "Wales":
        pdf = pdfplumber.open(local_pdf_file)
        for page in pdf.pages:
            try:
                table = page.extract_table(table_settings = {
                    # use text alignment since the table doesn't have lines
                    "vertical_strategy": "text", 
                    "horizontal_strategy": "text"
                })
                found_start = False
                output_rows = [["Date", "Country", "AreaCode", "Area", "TotalCases"]]
                for table_row in table:
                    if table_row[0] is not None and table_row[0].startswith("Aneurin"):
                        found_start = True
                    if found_start:
                        area = (normalize_whitespace(table_row[2])
                            .replace("Anglesey", "Isle of Anglesey")
                            .replace("ﬀ", "ff") # fix ligatures
                            .replace("ﬁ", "fi")
                        )
                        if area.startswith("Wales total"):
                            continue
                        area_code = lookup_local_authority_code(area)
                        cases = normalize_int(table_row[4])
                        output_row = [date, country, area_code, area, cases]
                        output_rows.append(output_row)
                    if table_row[2] is not None and normalize_whitespace(table_row[2]) == 'Resident outside Wales':
                        break
                return convert_wales_la_to_hb(date, country, output_rows)
            except IndexError:
                pass # no table on page
    return None


def convert_wales_la_to_hb(date, country, rows):
    output_rows = [["Date", "Country", "AreaCode", "Area", "TotalCases"]]
    def cases_for_one_la(la):
        return [row[4] for row in rows if row[3] == la][0]
    def cases_for(las):
        return sum([cases_for_one_la(la) for la in las])

    hb_to_las = {
        "Aneurin Bevan": [
            "Blaenau Gwent",
            "Caerphilly",
            "Monmouthshire",
            "Newport",
            "Torfaen"
        ],
        "Betsi Cadwaladr": [
            "Conwy",
            "Denbighshire",
            "Flintshire",
            "Gwynedd",
            "Isle of Anglesey",
            "Wrexham"
        ],
        "Cardiff and Vale": [
            "Cardiff",
            "Vale of Glamorgan"
        ],
        "Cwm Taf": [
            "Bridgend",
            "Merthyr Tydfil",
            "Rhondda Cynon Taf"
        ],
        "Hywel Dda": [
            "Carmarthenshire",
            "Ceredigion",
            "Pembrokeshire"
        ],
        "Powys": [
            "Powys"
        ],
        "Swansea Bay": [
            "Neath Port Talbot",
            "Swansea"
        ]
    }

    for (hb, las) in hb_to_las.items():
        output_rows.append([date, country, lookup_health_board_code(hb), hb, cases_for(las)])

    # append unknown/outside Wales etc
    for row in rows:
        if row[2] == "":
            output_rows.append(row)

    return output_rows


def save_daily_areas(date, country, rows):
    csv_file = "data/daily/covid-19-cases-{}-{}.csv".format(
        date, format_country(country)
    )
    with open(csv_file, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)


def save_daily_areas_to_sqlite(date, country, rows):
    with sqlite3.connect('data/covid-19-uk.db') as conn:
        c = conn.cursor()
        for row in rows[1:]:
            print(row)
            c.execute(f"INSERT OR REPLACE INTO cases VALUES ('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}')")

