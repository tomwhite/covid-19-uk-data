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
    df1 = convert("data/covid-19-totals-northern-ireland.csv", "Northern Ireland")
    df2 = convert("data/covid-19-totals-scotland.csv", "Scotland")
    df3 = convert("data/covid-19-totals-uk.csv", "UK")
    df4 = convert("data/covid-19-totals-wales.csv", "Wales")
    df = pd.concat([df1, df2, df3, df4]).sort_values(["Date", "Country", "Indicator"])
    df.to_csv("data/covid-19-indicators-uk-tmp.csv", index=False)
