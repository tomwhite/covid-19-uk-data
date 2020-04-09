#!/usr/bin/env python

import pandas as pd

def compare_uk_case_numbers():
    phe_cases_uk = pd.read_excel("data/raw/Historic COVID-19 Dashboard Data.xlsx", sheet_name="UK Cases", skiprows=8)
    phe_cases_uk["Date"] = phe_cases_uk["Date"].apply(lambda x: x.strftime('%Y-%m-%d')).astype(str)
    phe_cases_uk.set_index("Date")

    totals_uk = pd.read_csv("data/covid-19-totals-uk.csv")
    totals_uk = totals_uk[["Date", "ConfirmedCases"]].set_index("Date")

    compare_cases = pd.merge(totals_uk, phe_cases_uk, how="left", on="Date", right_index=False, left_index=False)
    compare_cases = compare_cases[compare_cases["Date"] >= '2020-01-31']
    compare_cases["Same"] = compare_cases["ConfirmedCases"] == compare_cases["Cumulative Cases"]
    compare_cases = compare_cases[compare_cases["Same"] == False]
    print(compare_cases)

def compare_country_case_numbers():
    phe_cases_countries = pd.read_excel("data/raw/Historic COVID-19 Dashboard Data.xlsx", sheet_name="Countries", skiprows=7)
    phe_cases_countries = phe_cases_countries.set_index("Area Name")
    phe_cases_countries = phe_cases_countries.drop(["Area Code"], axis=1).transpose()
    phe_cases_countries["Date"] = phe_cases_countries.index
    phe_cases_countries["Date"] = phe_cases_countries["Date"].apply(lambda x: x.strftime('%Y-%m-%d')).astype(str)
    phe_cases_countries.set_index("Date")
    # Check totals add up (internally)
    phe_cases_countries["Check"] = phe_cases_countries["UK"] == (phe_cases_countries["England "] + phe_cases_countries["Scotland"] + phe_cases_countries["Wales"] + phe_cases_countries["Northern Ireland"])
    #print(phe_cases_countries)

    # Load case numbers for this repo
    totals_uk = pd.read_csv("data/covid-19-totals-uk.csv")
    totals_uk = totals_uk[["Date", "ConfirmedCases"]].set_index("Date")

    totals_england = pd.read_csv("data/covid-19-totals-england.csv")
    totals_england = totals_england[["Date", "ConfirmedCases"]].set_index("Date")

    totals_wales = pd.read_csv("data/covid-19-totals-wales.csv")
    totals_wales = totals_wales[["Date", "ConfirmedCases"]].set_index("Date")

    totals_scotland = pd.read_csv("data/covid-19-totals-scotland.csv")
    totals_scotland = totals_scotland[["Date", "ConfirmedCases"]].set_index("Date")

    totals_ni = pd.read_csv("data/covid-19-totals-northern-ireland.csv")
    totals_ni = totals_ni[["Date", "ConfirmedCases"]].set_index("Date")

    totals_all_uk = totals_uk
    totals_all_uk = totals_all_uk.join(totals_england, how="left", rsuffix="_England")
    totals_all_uk = totals_all_uk.join(totals_wales, how="left", rsuffix="_Wales") 
    totals_all_uk.loc[totals_all_uk.index <= "2020-02-27", 'ConfirmedCases_Wales'] = 0
    totals_all_uk = totals_all_uk.join(totals_scotland, how="left", rsuffix="_Scotland")
    totals_all_uk = totals_all_uk.join(totals_ni, how="left", rsuffix="_NI")
    totals_all_uk.loc[totals_all_uk.index <= "2020-02-26", 'ConfirmedCases_NI'] = 0
    # Check totals add up (internally)
    totals_all_uk["Check"] = totals_all_uk["ConfirmedCases"] == (totals_all_uk["ConfirmedCases_England"] + totals_all_uk["ConfirmedCases_Scotland"] + totals_all_uk["ConfirmedCases_Wales"] + totals_all_uk["ConfirmedCases_NI"])
    #print(totals_all_uk)

    compare_all_cases = pd.merge(totals_all_uk, phe_cases_countries, how="left", on="Date", right_index=False, left_index=False)
    compare_all_cases = compare_all_cases[compare_all_cases["Date"] >= '2020-03-10']
    compare_all_cases["England_Same"] = compare_all_cases["ConfirmedCases_England"] == compare_all_cases["England "]
    compare_all_cases["Scotland_Same"] = compare_all_cases["ConfirmedCases_Scotland"] == compare_all_cases["Scotland"]
    compare_all_cases["Wales_Same"] = compare_all_cases["ConfirmedCases_Wales"] == compare_all_cases["Wales"]
    compare_all_cases["NI_Same"] = compare_all_cases["ConfirmedCases_NI"] == compare_all_cases["Northern Ireland"]
    compare_all_cases = compare_all_cases[(compare_all_cases["England_Same"] == False) | (compare_all_cases["Scotland_Same"] == False) | (compare_all_cases["Wales_Same"] == False) | (compare_all_cases["NI_Same"] == False)]
    #compare_all_cases = compare_all_cases[["Date", "England_Same", "Scotland_Same", "Wales_Same", "NI_Same"]]
    print(compare_all_cases)

def compare_utla_case_numbers():
    # PHE data
    phe_cases_utlas = pd.read_excel("data/raw/Historic COVID-19 Dashboard Data.xlsx", sheet_name="UTLAs", skiprows=7)

    def rename_datetimes(col_name):
        if isinstance(col_name, str):
            return col_name
        return col_name.strftime('%Y-%m-%d')

    phe_cases_utlas = phe_cases_utlas.rename(columns=rename_datetimes)
    phe_cases_utlas = phe_cases_utlas.rename(columns={"Area Code": "AreaCode"})

    phe_cases_utlas_tidy = pd.melt(phe_cases_utlas, id_vars=['AreaCode', 'Area Name'], value_vars=phe_cases_utlas.columns[2:], var_name='Date', value_name='Cases')
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
    phe_deaths = pd.read_excel("data/raw/Historic COVID-19 Dashboard Data.xlsx", sheet_name="UK Deaths", skiprows=7)
    phe_deaths["Date"] = phe_deaths["Date"].apply(lambda x: x.strftime('%Y-%m-%d')).astype(str)
    phe_deaths.set_index("Date")

    # Check totals add up (internally)
    phe_deaths["Check"] = phe_deaths["UK"] == (phe_deaths["England"] + phe_deaths["Scotland"] + phe_deaths["Wales"] + phe_deaths["Northern Ireland"])
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
    pd.set_option('display.max_rows', None)

    print("Compare PHE case numbers for all of UK with ones in this repo")
    compare_uk_case_numbers()

    print("Compare PHE case numbers for countries in UK with ones in this repo")
    compare_country_case_numbers()

    print("Compare PHE case numbers for England UTLAs with ones in this repo")
    compare_utla_case_numbers()

    print("Compare PHE deaths with ones in this repo")
    compare_deaths()
