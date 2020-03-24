from bs4 import BeautifulSoup
import csv
import dateparser
import math
import re
import sqlite3

from util import (
    format_country,
    is_blank,
    normalize_int,
    normalize_whitespace,
    lookup_health_board_code,
)

uk_pattern = re.compile(
    r"As of (?P<time>.+?) on (?P<date>.+?), (?P<tests>.+?) people have been tested in the (?P<country>.+?), of which (?P<negative_tests>.+?) were confirmed negative and (?P<positive_tests>.+?) were confirmed.+?positive."
)
wales_pattern = re.compile(
    r"(?s)Updated: (?P<time>.+?),? \S+ (?P<date>\d+\s\w+(\s\d{4})?).+? new cases have tested positive.+in (?P<country>.+?), bringing the total number of confirmed cases to (?P<positive_tests>\w+).+“(?P<deaths>.+?) people in Wales.+? died"
)
scotland_pattern = re.compile(
    r"(?s)Scottish test numbers: (?P<date>\d+\s\w+\s\d{4}).+?A total of (?P<tests>.+?) (?P<country>.+?) tests have concluded.+?(?P<negative_tests>[\d,]+?) tests were.+?negative.+?(?P<positive_tests>[\d,]+?) tests were.+?positive.+?(?P<deaths>.+?) patients?.+?have died"
)
ni_pattern = re.compile(
    r"(?s)As of (?P<time>.+?) on (?P<date>.+?), testing has resulted in .+? new positive cases,? bringing the total number of confirmed cases in (?P<country>.+?) to (?P<positive_tests>.+?)\..+?To date (?P<deaths>.+?) people who tested positive have sadly died\..*?The total number of tests completed in Northern Ireland is (?P<tests>.+?)\."
)


def get_text_from_html(html):
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text(separator=" ")
    text = normalize_whitespace(text)
    return text

def date_value_parser_fn(value):
    return dateparser.parse(value).strftime("%Y-%m-%d")


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
            return None
    return result

def parse_totals(country, html):
    text = get_text_from_html(html)
    if country == "UK":
        pattern_dict = {
            "Date": (r"As of (?P<Time>.+?) on (?P<Date>.+?),", date_value_parser_fn),
            "Tests": (r"As of (?P<Time>.+?) on (?P<Date>.+?), (a total of )?(?P<Tests>[\d,]+?) people have been tested", int_value_parser_fn),
            "ConfirmedCases": (r"and (?P<ConfirmedCases>[\d,]+?) were confirmed (as )?positive", int_value_parser_fn),
            "Deaths": (None, nan_value_parser_fn),
        }
        result = parse_totals_general(pattern_dict, country, text)
        return result
    elif country == "Scotland":
        pattern_dict = {
            "Date": (r"Scottish test numbers: (?P<Date>\d+\s\w+\s\d{4})", date_value_parser_fn),
            "Tests": (r"A total of (?P<Tests>.+?) Scottish tests have concluded", int_value_parser_fn),
            "ConfirmedCases": (r"(?P<ConfirmedCases>[\d,]+?) tests were (confirmed)?positive", int_value_parser_fn),
            "Deaths": (r"(?P<Deaths>\w+) patients?.+?have died", int_value_parser_fn),
        }
        result = parse_totals_general(pattern_dict, country, text)
        return result
    elif country == "Wales":
        pattern_dict = {
            "Date": (r"Updated: (?P<Time>.+?),? \S+ (?P<Date>\d+\s\w+(\s\d{4})?)", date_value_parser_fn),
            "Tests": (None, nan_value_parser_fn),
            "ConfirmedCases": (r"total number of confirmed cases to (?P<ConfirmedCases>\w+)", int_value_parser_fn),
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
            area = columns[0].replace("Ayrshire & Arran", "Ayrshire and Arran")
            area_code = lookup_health_board_code(area)
            cases = columns[1]
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
            if (
                columns[0] == "Health Board"
                or columns[0] == "Wales"
                or columns[0] == "TOTAL"
            ):
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
            cases = columns[-1]
            output_row = [date, country, lookup_health_board_code(area), area, cases]
            output_rows.append(output_row)
        return output_rows
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

