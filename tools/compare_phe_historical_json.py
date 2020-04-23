#!/usr/bin/env python

import json
import pandas as pd

phe_json_file = "data/raw/phe/coronavirus-covid-19-number-of-cases-in-uk-2020-04-22.json"

def load_json():
    with open(phe_json_file) as f:
        return json.load(f)

json_data = load_json()

def compare_uk_case_numbers():
    print("JSON file does not have historical UK case numbers")
    #print(json_data["overview"])


def compare_england_case_numbers():

    def total_confirmed_cases_df(country_code, country):
        cases = json_data["countries"][country_code]["dailyTotalConfirmedCases"]
        cases = {elt["date"]: [elt["value"]] for elt in cases}
        df = pd.DataFrame.from_dict(cases, orient='index', columns=[country])
        df["Date"] = df.index
        return df       

    phe_cases_england = total_confirmed_cases_df("E92000001", "England")

    # Load case numbers for this repo
    totals_england = pd.read_csv("data/covid-19-totals-england.csv")
    totals_england = totals_england[["Date", "ConfirmedCases"]].set_index("Date")

    compare_all_cases = pd.merge(totals_england, phe_cases_england, how="outer", on="Date", right_index=False, left_index=False).sort_values(by=['Date'])
    compare_all_cases["Same"] = compare_all_cases["ConfirmedCases"] == compare_all_cases["England"]
    print(compare_all_cases)


def compare_utla_case_numbers():

    # PHE data
    def total_confirmed_cases_df(utla_code, utla):
        cases = json_data["utlas"][utla_code]["dailyTotalConfirmedCases"]
        cases = {elt["date"]: [elt["value"]] for elt in cases}
        df = pd.DataFrame.from_dict(cases, orient='index', columns=["Cases"])
        df["Date"] = df.index
        df["AreaCode"] = utla_code
        df["Area"] = utla
        return df      

    all_cases_dfs = []
    for utla_code in json_data["utlas"].keys():
        cases = total_confirmed_cases_df(utla_code, json_data["utlas"][utla_code]["name"]["value"])
        all_cases_dfs.append(cases)
    phe_cases_utlas_tidy = pd.concat(all_cases_dfs, ignore_index=True)
    #print(phe_cases_utlas_tidy)

    # Data from this repo
    cases_uk = pd.read_csv("data/covid-19-cases-uk.csv")
    cases_uk = cases_uk[cases_uk["Date"] >= "2020-03-06"] # filter out rows with "1 to 4" etc
    cases_uk = cases_uk[cases_uk["TotalCases"].notnull()] # filter out rows with NaN (meaning <5 for Scotland)
    cases_uk = cases_uk.astype({"TotalCases": "int64"})
    #print(cases_uk)
    
    merged = pd.merge(cases_uk, phe_cases_utlas_tidy, how="inner", on=["Date", "AreaCode"], right_index=False, left_index=False)
    merged["CasesDiff"] = merged["TotalCases"] - merged["Cases"]
    merged = merged[merged["CasesDiff"] != 0]
    print(merged)


def compare_deaths():

    def total_deaths_df(country_code, country):
        if country_code == "K02000001":
            cases = json_data["overview"][country_code]["dailyTotalDeaths"]
        else:
            cases = json_data["countries"][country_code]["dailyTotalDeaths"]
        cases = {elt["date"]: [elt["value"]] for elt in cases}
        df = pd.DataFrame.from_dict(cases, orient='index', columns=[country])
        df["Date"] = df.index
        return df  

    phe_deaths = total_deaths_df("K02000001", "United Kingdom")
    phe_deaths = pd.merge(phe_deaths, total_deaths_df("E92000001", "England"), how="outer", on="Date", right_index=False, left_index=False)
    phe_deaths = pd.merge(phe_deaths, total_deaths_df("S92000003", "Scotland"), how="outer", on="Date", right_index=False, left_index=False)
    phe_deaths = pd.merge(phe_deaths, total_deaths_df("W92000004", "Wales"), how="outer", on="Date", right_index=False, left_index=False)
    phe_deaths = pd.merge(phe_deaths, total_deaths_df("N92000002", "Northern Ireland"), how="outer", on="Date", right_index=False, left_index=False)
    phe_deaths.set_index("Date")

    # Check totals add up (internally)
    phe_deaths["Check"] = phe_deaths["United Kingdom"] == (phe_deaths["England"] + phe_deaths["Scotland"] + phe_deaths["Wales"] + phe_deaths["Northern Ireland"])
    #print(phe_deaths)

    # Load case numbers for this repo
    indicators_uk = pd.read_csv("data/covid-19-indicators-uk.csv")
    indicators_uk = indicators_uk[indicators_uk["Indicator"] == "Deaths"]
    indicators_uk = indicators_uk.pivot(index='Date', columns='Country', values='Value')
    #print(indicators_uk)

    compare_deaths = pd.merge(indicators_uk, phe_deaths, how="inner", on="Date", right_index=False, left_index=False, suffixes=("", "_phe"))
    compare_deaths = compare_deaths[compare_deaths["Date"] >= '2020-03-27']
    compare_deaths["England_Same"] = compare_deaths["England"] == compare_deaths["England_phe"]
    compare_deaths["Scotland_Same"] = compare_deaths["Scotland"] == compare_deaths["Scotland_phe"]
    compare_deaths["Wales_Same"] = compare_deaths["Wales"] == compare_deaths["Wales_phe"]
    compare_deaths["NI_Same"] = compare_deaths["Northern Ireland"] == compare_deaths["Northern Ireland_phe"]
    compare_deaths = compare_deaths[(compare_deaths["England_Same"] == False) | (compare_deaths["Scotland_Same"] == False) | (compare_deaths["Wales_Same"] == False) | (compare_deaths["NI_Same"] == False)]
    print(compare_deaths)

if __name__ == "__main__":
    #pd.set_option('display.max_rows', None)

    print("Compare PHE case numbers for all of UK with ones in this repo")
    compare_uk_case_numbers()

    print("Compare PHE case numbers England with ones in this repo")
    compare_england_case_numbers()

    print("Compare PHE case numbers for England UTLAs with ones in this repo")
    compare_utla_case_numbers()

    print("Compare PHE deaths with ones in this repo")
    compare_deaths()
