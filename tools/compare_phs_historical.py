#!/usr/bin/env python

import pandas as pd

# Download file from https://www.gov.scot/publications/trends-in-number-of-people-in-hospital-with-confirmed-or-suspected-covid-19/

def compare_scotland_testing_and_case_numbers():
    phs_testing = pd.read_excel("data/raw/phs/HSCA+-+SG+Website+-+Indicator+Trends+for+daily+data+publication.xlsx", sheet_name="Table 5 - Testing", skiprows=3)
    phs_testing = phs_testing.rename(columns={"Unnamed: 0": "Date"})
    phs_testing["Date"] = phs_testing["Date"].apply(lambda x: x.strftime('%Y-%m-%d')).astype(str)
    phs_testing = phs_testing[["Date", "Positive", "Total"]]
    print(phs_testing)

    totals_scotland = pd.read_csv("data/covid-19-totals-scotland.csv")
    totals_scotland = totals_scotland[["Date", "Tests", "ConfirmedCases"]]
    print(totals_scotland)

    compare_all_cases = pd.merge(totals_scotland, phs_testing, how="outer", on="Date", right_index=False, left_index=False).sort_values(by=['Date'])
    compare_all_cases["Tests_Same"] = compare_all_cases["Tests"] == compare_all_cases["Total"]
    compare_all_cases["Cases_Same"] = compare_all_cases["ConfirmedCases"] == compare_all_cases["Positive"]
    print(compare_all_cases)

if __name__ == "__main__":
    pd.set_option('display.max_rows', None)

    print("Compare Scotland testing and case numbers with ones in this repo")
    compare_scotland_testing_and_case_numbers()
