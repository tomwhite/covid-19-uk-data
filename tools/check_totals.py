#!/usr/bin/env python

# Check that the area case numbers add up to the totals.

import pandas as pd


def check_latest(totals_csv_file, cases_csv_file, country):
    totals = pd.read_csv(totals_csv_file)
    last_row = totals.to_dict("records")[-1]
    date = last_row["Date"]
    total_cases = last_row["ConfirmedCases"]

    cases_uk = pd.read_csv(cases_csv_file)
    cases_uk_on_date = cases_uk[
        (cases_uk["Date"] == date) & (cases_uk["Country"] == country)
    ]
    cases_uk_on_date = cases_uk_on_date.astype({"TotalCases": "int64"})
    total_cases_check = cases_uk_on_date["TotalCases"].sum()

    if total_cases == total_cases_check:
        print(
            "Total cases for {} on {} checks out at {}".format(
                country, date, total_cases
            )
        )
    else:
        print(
            "Mismatch. Total cases for {} on {} is {} from {} and {} from {}".format(
                country,
                date,
                total_cases,
                totals_csv_file,
                total_cases_check,
                cases_csv_file,
            )
        )


if __name__ == "__main__":
    check_latest(
        "data/covid-19-totals-scotland.csv", "data/covid-19-cases-uk.csv", "Scotland"
    )
    check_latest(
        "data/covid-19-totals-wales.csv", "data/covid-19-cases-uk.csv", "Wales"
    )
