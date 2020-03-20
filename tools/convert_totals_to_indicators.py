#!/usr/bin/env python

# Convert deprecated totals files to indicators file.

import pandas as pd


def convert(totals_csv_file, country):
    totals = pd.read_csv(totals_csv_file)
    totals["Country"] = country
    totals_tidy = totals.melt(
        id_vars=["Date", "Country"],
        value_vars=["Tests", "ConfirmedCases", "Deaths"],
        var_name="Indicator",
        value_name="Value",
    ).dropna()
    totals_tidy = totals_tidy.astype({"Value": "int64"})
    return totals_tidy


if __name__ == "__main__":
    dfs = [
        convert("data/covid-19-totals-england.csv", "England"),
        convert("data/covid-19-totals-northern-ireland.csv", "Northern Ireland"),
        convert("data/covid-19-totals-scotland.csv", "Scotland"),
        convert("data/covid-19-totals-uk.csv", "UK"),
        convert("data/covid-19-totals-wales.csv", "Wales"),
    ]
    df = pd.concat(dfs).sort_values(["Date", "Country", "Indicator"])
    df.to_csv("data/covid-19-indicators-uk.csv", index=False)
