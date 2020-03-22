#!/usr/bin/env python

# Generate all CSV files from the sqlite database

import pandas as pd
import sqlite3

import math
import pandas as pd

from util import camel_to_hyphens, format_country, format_int

# import csvs with:
# rm data/covid-19-uk.db
# csvs-to-sqlite --replace-tables -t indicators -pk Date -pk Country -pk Indicator data/covid-19-indicators-uk.csv data/covid-19-uk.db
# csvs-to-sqlite --replace-tables -t cases -pk Date -pk Country -pk AreaCode -pk Area data/covid-19-cases-uk.csv data/covid-19-uk.db

# simple query
# with sqlite3.connect('covid-19-uk.db') as conn:
#     c = conn.cursor()
#     for row in c.execute('SELECT * FROM "covid-19-totals-uk" ORDER BY Date'):
#         print(row)

# insert a row if it doesn't already exist, or update value if it does
# with sqlite3.connect('data/covid-19-uk.db') as conn:
#     c = conn.cursor()
#     result = {'Date': '2020-03-22', 'Country': "England", 'Indicator': "Tests", "Value": 16}
#     c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{result['Date']}', '{result['Country']}', '{result['Indicator']}', {result['Value']})")


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
        df.to_csv("data/covid-19-cases-uk.csv", index=False)

    # convert indicators csv to totals csvs
    convert("data/covid-19-indicators-uk.csv")
