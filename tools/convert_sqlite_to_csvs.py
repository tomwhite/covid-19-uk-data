#!/usr/bin/env python

# Generate all CSV files from the sqlite database

import csv
import pandas as pd
import sqlite3

import math
import pandas as pd

from util import camel_to_hyphens, format_country, format_int

def format_int_with_nan(val):
    if val == "NaN" or val == "nan" or math.isnan(val):
        return "NaN"
    return int(val)

def convert(indicators_csv_file):
    indicators = pd.read_csv(indicators_csv_file)

    for country in ["England", "Northern Ireland", "Scotland", "UK", "Wales"]:
        wide = indicators[indicators["Country"] == country]
        wide = wide.pivot(index="Date", columns="Indicator", values="Value")
        wide = wide.reindex(columns=["Tests", "ConfirmedCases", "Deaths"])

        # don't use to_csv since pandas can't write NA ints
        with open(
            "data/covid-19-totals-{}.csv".format(format_country(country)), "w"
        ) as f:
            f.write("Date,Tests,ConfirmedCases,Deaths\n")
            for (i, d) in wide.to_dict("index").items():
                f.write(
                    "{},{},{},{}\n".format(
                        i,
                        format_int(d["Tests"]),
                        format_int(d["ConfirmedCases"]),
                        format_int(d["Deaths"]),
                    )
                )


if __name__ == "__main__":

    # export from sqlite to indicators csv
    with sqlite3.connect('data/covid-19-uk.db') as conn:
        df = pd.read_sql('SELECT * FROM indicators ORDER BY Date, Country, Indicator', conn)
        df.to_csv("data/covid-19-indicators-uk.csv", index=False)

    # export from sqlite to cases csv
    with sqlite3.connect('data/covid-19-uk.db') as conn:
        df = pd.read_sql('SELECT * FROM cases ORDER BY Date, Country, rowid', conn)

        # don't use to_csv since pandas can't write NA ints
        with open("data/covid-19-cases-uk.csv", "w") as csvfile:
            csvfile.write("Date,Country,AreaCode,Area,TotalCases\n")
            writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for (i, d) in df.to_dict("index").items():
                writer.writerow([
                    d["Date"],
                    d["Country"],
                    d["AreaCode"] if d["AreaCode"] is not None else "",
                    d["Area"],
                    format_int_with_nan(d["TotalCases"])
                ])

    # convert indicators csv to totals csvs
    convert("data/covid-19-indicators-uk.csv")
