from bs4 import BeautifulSoup
import csv
import dateparser
import math
import re

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
    r"(?s)Updated: (?P<time>.+?),? \S+ (?P<date>\d+\s\w+\s\d{4}).+? new cases have tested positive.+in (?P<country>.+?), bringing the total number of confirmed cases to (?P<positive_tests>\w+).+“(?P<deaths>.+?) people in Wales.+? died"
)
scotland_pattern = re.compile(
    r"(?s)Scottish test numbers: (?P<date>\d+\s\w+\s\d{4}).+?A total of (?P<tests>.+?) (?P<country>.+?) tests have concluded.+?(?P<negative_tests>[\d,]+?) tests were.+?negative.+?(?P<positive_tests>[\d,]+?) tests were.+?positive.+?(?P<deaths>.+?) patients?.+?have died"
)
ni_pattern = re.compile(
    r"(?s)As of (?P<time>.+?) on (?P<date>.+?), testing has resulted in .+? new positive cases,? bringing the total number of confirmed cases in (?P<country>.+?) to (?P<positive_tests>.+?)\..+?To date (?P<deaths>.+?) person who tested positive has sadly died\..*?The total number of tests completed in Northern Ireland is (?P<tests>.+?)\."
)


def get_text_from_html(html):
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.get_text()
    text = text.replace(
        u"\xa0", u" "
    )  # replace non-breaking spaces with regular spaces
    return text


def parse_totals(country, html):
    text = get_text_from_html(html)
    if country == "UK":
        pattern = uk_pattern
    elif country == "Scotland":
        pattern = scotland_pattern
    elif country == "Wales":
        pattern = wales_pattern
    elif country == "Northern Ireland":
        pattern = ni_pattern
    m = re.search(pattern, text)
    if m is not None:
        groups = m.groupdict()
        date = dateparser.parse(groups["date"]).strftime("%Y-%m-%d")
        country = normalize_whitespace(groups.get("country")).replace(
            "Scottish", "Scotland"
        )
        tests = normalize_int(groups.get("tests", float("nan")))
        positive_tests = normalize_int(groups["positive_tests"])
        negative_tests = normalize_int(groups.get("negative_tests", float("nan")))
        deaths = normalize_int(groups.get("deaths", float("nan")))

        return {
            "Date": date,
            "Country": country,
            "Tests": tests,
            "ConfirmedCases": positive_tests,
            "Deaths": deaths,
        }
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


def parse_daily_areas(date, country, html):
    if country in ("Northern Ireland", "UK"):
        return None
    soup = BeautifulSoup(html, features="html.parser")
    table = soup.find_all("table")[-1]
    output_rows = [["Date", "Country", "AreaCode", "Area", "TotalCases"]]
    if country == "Scotland":
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
            if is_blank(columns[2]):
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
            cases = columns[2]
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
