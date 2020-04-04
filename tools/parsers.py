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
            "Date": (r"As of (?P<Time>.+?) on (?P<Date>.+?),", date_value_parser_fn),
            "Tests": (r"As of (?P<Time>.+?) on (?P<Date>.+?), (a total of )?(?P<Tests>[\d,]+?) people have been tested", int_value_parser_fn),
            "ConfirmedCases": (r"(and|of which) (?P<ConfirmedCases>[\d,]+?) were confirmed (as )?positive", int_value_parser_fn),
            "Deaths": (r"(?P<Deaths>[\d,]+) (patients?.+?)?have died", int_value_parser_fn),
        }
        result = parse_totals_general(pattern_dict, country, text)
        return result
    elif country == "Scotland":
        pattern_dict = {
            "Date": (r"Scottish test numbers: (?P<Date>\d+\s\w+\s\d{4})", date_value_parser_fn),
            "Tests": (r"total of (?P<Tests>.+?) (Scottish tests have concluded|people in Scotland have been tested)", int_value_parser_fn),
            "ConfirmedCases": (r"(?P<ConfirmedCases>[\d,]+?) tests were (confirmed)?positive", int_value_parser_fn),
            "Deaths": (r"(?P<Deaths>\w+) patients?.+?have died", int_value_parser_fn),
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


def get_text_from_pdf(local_pdf_file):
    pdf = pdfplumber.open(local_pdf_file)
    page = pdf.pages[0] # just extract first page
    text = page.extract_text()
    text = normalize_whitespace(text)
    return text


def parse_totals_pdf_text(country, text):
    if country == "Northern Ireland":
        pattern_dict = {
            "Date": (r"Date generated: (?P<Date>[\d,]+/[\d,]+/[\d,]+)", date_value_parser_fn),
            "Tests": (r"Number of Individuals tested( for COVID-19| for SARS-COV2 Virus)?:? (?P<Tests>[\d,]+)", int_value_parser_fn),
            "ConfirmedCases": (r"(Number of Individuals (with confirmed|testing positive for) (COVID-19|SARS-COV2 Virus)|Cumulative number of laboratory confirmed COVID-19 cases):? (?P<ConfirmedCases>[\d,]+)", int_value_parser_fn),
            "Deaths": (r"(Total|Cumulative) number of (Trust |reported )?deaths( associated with COVID-19)?: (?P<Deaths>[\d,]+)", int_value_parser_fn),
        }
        result = parse_totals_general(pattern_dict, country, text)
        return result

def print_totals(results):
    date = results["Date"]
    country = results["Country"]
    tests = results["Tests"]
    confirmed_cases = results["ConfirmedCases"]
    deaths = results["Deaths"]
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
    deaths = results["Deaths"]
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
    deaths = results["Deaths"]
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
        table = soup.find_all("table")[-1]
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
            cases = columns[1].replace("*", "")
            output_row = [date, country, area_code, area, cases]
            output_rows.append(output_row)
        return output_rows
    elif country == "Wales":
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
                .strip()
            )
            if is_blank(area):
                area = columns[0]
            cases = columns[-1].replace("*","")
            output_row = [date, country, lookup_health_board_code(area), area, cases]
            output_rows.append(output_row)
        return output_rows
    return None


def parse_daily_areas_pdf(date, country, local_pdf_file):
    if country == "Northern Ireland":
        pdf = pdfplumber.open(local_pdf_file)
        for page in pdf.pages:
            try:
                table = page.extract_table()
                if table[0][0] == "Local Government District":
                    output_rows = [["Date", "Country", "AreaCode", "Area", "TotalCases"]]
                    for table_row in table[1:]:
                        if table_row[0].lower() == "total":
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
    return None


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
            c.execute(f"INSERT OR REPLACE INTO cases VALUES ('{row[0]}', '{row[1]}', '{row[2]}', '{row[3]}', {row[4]})")

