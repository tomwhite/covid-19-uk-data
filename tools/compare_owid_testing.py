#!/usr/bin/env python

from bs4 import BeautifulSoup
import glob
import pandas as pd
import re
import sys

from parsers import parse_totals, parse_tests

from util import normalize_int

def is_testing_table(table):
    headers = [th.text for th in table.findAll("th")]
    return "Tests" in headers

# Use the historical HTML files to generate a CSV.
# Some pages cannot be handled by the parser so they are filled in manually.
def generate_csv():
    print("Date,Country,DailyTestsPerformed,TotalTestsPerformed,DailyPeopleTested,TotalPeopleTested")
    for file in sorted(glob.glob("data/raw/coronavirus-covid-19-number-of-cases-in-uk-*.html")):
        m = re.match(r".+(\d{4}-\d{2}-\d{2})\.html", file)
        date = m.group(1)
        with open(file) as f:
            html = f.read()

        if date <= "2020-03-22":
            # older pages cannot be parsed with current parser
            continue

        if date <= "2020-04-07":
            result = parse_totals("UK", html)
            print("{},UK,,,,{}".format(date, result["Tests"]))
            continue

        result = parse_tests("UK", html)
        output_row = [date, "UK", result["DailyTestsPerformed"], result["TotalTestsPerformed"], result["DailyPeopleTested"], result["TotalPeopleTested"]]
        print(",".join([str(val) for val in output_row]))

def load_owid():
    use_local = False
    if use_local:
        file = "data/raw/owid/covid-testing-all-observations.csv"
    else:
        file = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/testing/covid-testing-all-observations.csv"
    df = pd.read_csv(file)
    df = df[(df["Entity"] == "United Kingdom - people tested") | (df["Entity"] == "United Kingdom - tests performed")]
    df = df[["Date", "Entity", "Cumulative total", "Daily change in cumulative total"]]
    df.rename(columns={"Cumulative total": "Total", "Daily change in cumulative total": "Daily"}, inplace=True)
    df = df.replace({"Entity": {
        "United Kingdom - people tested": "PeopleTested",
        "United Kingdom - tests performed": "TestsPerformed"
    }})
    df = df.melt(id_vars=["Date", "Entity"], value_vars=["Total", "Daily"])
    df["VarEntity"] = df["variable"] + df["Entity"]
    df = df.pivot(index="Date", columns="VarEntity", values="value")
    return df

def compare():
    local = pd.read_csv("data/covid-19-tests-uk.csv")
    owid = load_owid()

    compare_tests = pd.merge(local, owid, how="inner", on="Date", right_index=False, left_index=False, suffixes=("", "_owid"))
    compare_tests.drop(columns=["Country"], inplace=True)

    compare_people = compare_tests[["Date", "DailyPeopleTested", "TotalPeopleTested", "DailyPeopleTested_owid", "TotalPeopleTested_owid"]]
    compare_people["DailyPeopleTestedSame"] = compare_people["DailyPeopleTested"] == compare_people["DailyPeopleTested_owid"]
    compare_people["TotalPeopleTestedSame"] = compare_people["TotalPeopleTested"] == compare_people["TotalPeopleTested_owid"]
      
    print(compare_people)

    compare_tests = compare_tests[["Date", "DailyTestsPerformed", "TotalTestsPerformed", "DailyTestsPerformed_owid", "TotalTestsPerformed_owid"]]
    compare_tests["DailyTestsPerformedSame"] = compare_tests["DailyTestsPerformed"] == compare_tests["DailyTestsPerformed_owid"]
    compare_tests["TotalTestsPerformedSame"] = compare_tests["TotalTestsPerformed"] == compare_tests["TotalTestsPerformed_owid"]

    print(compare_tests)


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)

    generate_csv()

    load_owid()
    compare()
