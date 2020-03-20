#!/usr/bin/env python

# Check that the area case numbers add up to the totals.

import pandas as pd


def check_latest(indicators_csv_file, cases_csv_file, country):
    indicators = pd.read_csv(indicators_csv_file)
    indicators = indicators[
        (indicators["Country"] == country)
        & (indicators["Indicator"] == "ConfirmedCases")
    ]

    cases_uk = pd.read_csv(cases_csv_file)
    cases_uk = cases_uk[cases_uk["Country"] == country]
    cases_uk = cases_uk.astype({"TotalCases": "int64"})
    cases_uk = cases_uk.groupby("Date").sum()

    df = cases_uk.join(indicators.set_index('Date'))
    df = df[df["TotalCases"] != df["Value"]]

    if len(df) == 0:
        print("Total cases for {} checks out".format(country))
    else:
        print("Mismatch for {}".format(country))
        print(df)


if __name__ == "__main__":
    check_latest(
        "data/covid-19-indicators-uk.csv", "data/covid-19-cases-uk.csv", "Scotland"
    )
    check_latest(
        "data/covid-19-indicators-uk.csv", "data/covid-19-cases-uk.csv", "Wales"
    )
