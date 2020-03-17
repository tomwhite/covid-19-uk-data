#!/usr/bin/env python

# Sort the indicators file.

import pandas as pd


if __name__ == "__main__":
    csv_in_file = "data/covid-19-indicators-uk.csv"
    df = pd.read_csv(csv_in_file)
    df = df.sort_values(["Date", "Country", "Indicator"])
    df.to_csv(csv_in_file, index=False)
