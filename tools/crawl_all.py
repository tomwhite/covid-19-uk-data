#!/usr/bin/env python

# Crawls all the historical data in one go. This ensures that revisions of old data are accounted for.

import dateparser
import datetime
import json
import math
import numpy as np
import os
import pandas as pd
import requests
import sqlite3
import sys
import xmltodict

from crawl import get_json_url
from parsers import (
    parse_daily_areas_json,
    save_daily_areas,
    save_daily_areas_to_sqlite,
)
from util import format_country, la_to_hb, lookup_health_board_code, read_json

def save_indicator_to_sqlite(date, country, indicator, value):
    with sqlite3.connect('data/covid-19-uk.db') as conn:
        c = conn.cursor()
        c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', '{country}', '{indicator}', {value})")

def save_indicators_df_to_sqlite(df, country, indicator):
    with sqlite3.connect('data/covid-19-uk.db') as conn:
        c = conn.cursor()
        # Clear out old data?
        #c.execute(f"DELETE FROM indicators WHERE Country = '{country}' AND Indicator = '{indicator}'")
        for index, row in df.iterrows():
            date = row["Date"]
            value = row[indicator]
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', '{country}', '{indicator}', {value})")

def save_cases_df_to_sqlite(df, country):
    with sqlite3.connect('data/covid-19-uk.db') as conn:
        c = conn.cursor()
        c.execute(f"DELETE FROM cases WHERE Country = '{country}'")
        for index, row in df.iterrows():
            date = row["Date"]
            area_code = row["AreaCode"]
            area = row["Area"]
            value = row["TotalCases"]
            c.execute(f"INSERT OR REPLACE INTO cases VALUES ('{date}', '{country}', '{area_code}', '{area}', '{value}')")

# Use Our World In Data for some UK stats that are not included in PHE's CSV or JSON files
# UK historical test numbers (people tested)
def crawl_owid(use_local=False):
    if use_local:
        file = "data/raw/owid/covid-testing-all-observations.csv"
    else:
        file = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/testing/covid-testing-all-observations.csv"
    df = pd.read_csv(file)
    df = df[df["Entity"] == "United Kingdom - people tested"]
    df = df[["Date", "Cumulative total"]]
    df.rename(columns={"Cumulative total": "Tests"}, inplace=True)
    save_indicators_df_to_sqlite(df, "UK", "Tests")

    # Not used due to data mismatch
    # UK historical confirmed cases
    # if use_local:
    #     file = "data/raw/owid/total_cases.csv"
    # else:
    #     file = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/ecdc/total_cases.csv"
    # df = pd.read_csv(file)
    # df = df[["date", "United Kingdom"]]
    # df.rename(columns={"date": "Date", "United Kingdom": "ConfirmedCases"}, inplace=True)
    # save_indicators_df_to_sqlite(df, "UK", "ConfirmedCases")


# UK (and all nations) historical deaths
# England historical confirmed cases
# England UTLAs historical confirmed cases
def crawl_phe(use_local=False):
    if use_local:
        file = "data/raw/phe/data_latest.json"
    else:
        file = "https://coronavirus.data.gov.uk/downloads/data/data_latest.json"

    json_data = read_json(file)

    def total_deaths_df(country_code, country):
        if country_code == "K02000001":
            cases = json_data["overview"][country_code]["dailyTotalDeaths"]
        else:
            cases = json_data["countries"][country_code]["dailyTotalDeaths"]
        cases = {elt["date"]: [elt["value"]] for elt in cases}
        df = pd.DataFrame.from_dict(cases, orient='index', columns=[country])
        df["Date"] = df.index
        df.rename(columns={country: "Deaths"}, inplace=True)
        return df

    df = total_deaths_df("K02000001", "United Kingdom")
    save_indicators_df_to_sqlite(df, "UK", "Deaths")

    df = total_deaths_df("E92000001", "England")
    save_indicators_df_to_sqlite(df, "England", "Deaths")

    # Found from PHS data instead
    # df = total_deaths_df("S92000003", "Scotland")
    # save_indicators_df_to_sqlite(df, "Scotland", "Deaths")

    # TBD
    # df = total_deaths_df("W92000004", "Wales")
    # save_indicators_df_to_sqlite(df, "Wales", "Deaths")

    # TBD
    # df = total_deaths_df("N92000002", "Northern Ireland")
    # save_indicators_df_to_sqlite(df, "Northern Ireland", "Deaths")

    # Get UK ConfirmedCases, but only latest value since historical data is not available
    # last_updated = json_data["lastUpdatedAt"]
    # last_updated_date = last_updated.split("T")[0]
    # uk_cases = json_data["overview"]["K02000001"]["totalCases"]["value"]
    # save_indicator_to_sqlite(last_updated_date, "UK", "ConfirmedCases", uk_cases)

    def total_confirmed_cases_country_df(country_code, country):
        cases = json_data["countries"][country_code]["dailyTotalConfirmedCases"]
        cases = {elt["date"]: [elt["value"]] for elt in cases}
        df = pd.DataFrame.from_dict(cases, orient='index', columns=[country])
        df["Date"] = df.index
        df.rename(columns={country: "ConfirmedCases"}, inplace=True)
        return df

    df = total_confirmed_cases_country_df("E92000001", "England")
    save_indicators_df_to_sqlite(df, "England", "ConfirmedCases")

    def total_confirmed_cases_utla_df(utla_code, utla):
        cases = json_data["utlas"][utla_code]["dailyTotalConfirmedCases"]
        cases = {elt["date"]: [elt["value"]] for elt in cases}
        df = pd.DataFrame.from_dict(cases, orient='index', columns=["TotalCases"])
        df["Date"] = df.index
        df["AreaCode"] = utla_code
        df["Area"] = utla
        df["Country"] = "England"
        df = df[["Date", "Country", "AreaCode", "Area", "TotalCases"]]
        return df

    all_cases_dfs = []
    for utla_code in json_data["utlas"].keys():
        cases = total_confirmed_cases_utla_df(utla_code, json_data["utlas"][utla_code]["name"]["value"])
        all_cases_dfs.append(cases)
    area_cases = pd.concat(all_cases_dfs, ignore_index=True)
    save_cases_df_to_sqlite(area_cases, "England")


# Scotland historical test numbers
# Scotland historical confirmed cases
# Scotland historical deaths
# Scotland health board historical confirmed cases
def crawl_phs(use_local=False):
    if not use_local:
        urls = get_phs_xlsx_urls()

    if use_local:
        file = "data/raw/phs/HSCA+-+SG+Website+-+Indicator+Trends+for+daily+data+publication.xlsx"
    else:
        file = urls["totals"]

    df = pd.read_excel(file, sheet_name="Table 5 - Testing", skiprows=3)
    df.rename(columns={"Unnamed: 0": "Date"}, inplace=True)
    df["Date"] = df["Date"].apply(lambda x: x.strftime('%Y-%m-%d')).astype(str)
    df = df[["Date", "Positive", "Total"]]
    df.rename(columns={"Total": "Tests", "Positive": "ConfirmedCases"}, inplace=True)
    save_indicators_df_to_sqlite(df, "Scotland", "Tests")
    save_indicators_df_to_sqlite(df, "Scotland", "ConfirmedCases")

    df = pd.read_excel(file, sheet_name="Table 8 - Deaths", skiprows=2)
    df.rename(columns={"Number of COVID-19 confirmed deaths registered to date": "Deaths"}, inplace=True)
    df["Date"] = df["Date"].apply(lambda x: x.strftime('%Y-%m-%d')).astype(str)
    save_indicators_df_to_sqlite(df, "Scotland", "Deaths")

    if use_local:
        file = "data/raw/phs/Board-level+figures+-+FOR+ONLINE+PUBLICATION.xlsx"
    else:
        file = urls["areas"]

    df = pd.read_excel(file, sheet_name="Table 1 - Cumulative cases", skiprows=2)
    df["Date"] = df["Date"].apply(lambda x: x.strftime('%Y-%m-%d')).astype(str)
    df = df.drop(columns=['Scotland'])
    area_cases = df.melt(id_vars=["Date"], var_name="Area", value_name="TotalCases")
    area_cases = area_cases.replace("*", "NaN")
    area_cases["Area"] = area_cases["Area"].apply(lambda hb: hb.replace("NHS", "").replace("&", "and").strip())
    area_cases["AreaCode"] = area_cases["Area"].apply(lambda hb: lookup_health_board_code(hb))
    area_cases["Country"] = "Scotland"
    area_cases = area_cases[["Date", "Country", "AreaCode", "Area", "TotalCases"]]
    save_cases_df_to_sqlite(area_cases, "Scotland")

def get_phs_xlsx_urls():
    # URLs have dates embedded in them, so scrape them from HTML page
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    url = "https://www.gov.scot/publications/trends-in-number-of-people-in-hospital-with-confirmed-or-suspected-covid-19/"
    html = requests.get(url).text
    soup = BeautifulSoup(html, features="html.parser")
    urls = {}
    for link in soup.findAll("a"):
        if link.get_text().startswith("Trends in daily COVID-19 data"):
            urls["totals"] = urljoin(url, link.get("href"))
        elif link.get_text().startswith("COVID-19 data by NHS Board"):
            urls["areas"] = urljoin(url, link.get("href"))
    return urls

# Wales historical test numbers
# Wales historical confirmed cases
# Wales historical deaths
# Wales health board historical confirmed cases
def crawl_phw(use_local=False):
    if use_local:
        file = "data/raw/phw/Rapid COVID-19 surveillance data.xlsx"
    else:
        file = "http://www2.nphs.wales.nhs.uk:8080/CommunitySurveillanceDocs.nsf/61c1e930f9121fd080256f2a004937ed/77fdb9a33544aee88025855100300cab/$FILE/Rapid%20COVID-19%20surveillance%20data.xlsx"

    df = pd.read_excel(file, sheet_name="Tests by specimen date")
    df["Date"] = df["Specimen date"].apply(lambda x: x.strftime('%Y-%m-%d')).astype(str)
    df.rename(columns={"Cumulative testing episodes": "Tests", "Cumulative cases": "ConfirmedCases"}, inplace=True)

    tests = df.groupby("Date", as_index=False)[["Tests"]].sum()
    cases = df.groupby("Date", as_index=False)[["ConfirmedCases"]].sum()

    # TBD
    #save_indicators_df_to_sqlite(tests, "Wales", "Tests")
    #save_indicators_df_to_sqlite(cases, "Wales", "ConfirmedCases")

    def lookup_hb(la):
        hb = la_to_hb(la)
        if hb is None:
            return la
        return hb

    df.rename(columns={"ConfirmedCases": "TotalCases"}, inplace=True)
    df["Area"] = df["Local Authority"].apply(lambda la: lookup_hb(la))
    area_cases = df.groupby(["Date", "Area"], as_index=False)[["TotalCases"]].sum()
    area_cases["AreaCode"] = area_cases["Area"].apply(lambda hb: lookup_health_board_code(hb))
    area_cases["Country"] = "Wales"
    area_cases = area_cases[["Date", "Country", "AreaCode", "Area", "TotalCases"]]
    # TBD
    #save_cases_df_to_sqlite(area_cases, "Wales")

    df = pd.read_excel(file, sheet_name="Deaths by date")
    df["Date"] = df["Date of death"].apply(lambda x: x.strftime('%Y-%m-%d')).astype(str)
    df.rename(columns={"Cumulative deaths": "Deaths"}, inplace=True)
    save_indicators_df_to_sqlite(df, "Wales", "Deaths")


if __name__ == "__main__":
    #pd.set_option('display.max_rows', None)

    use_local = False

    if len(sys.argv) == 2:
        source = sys.argv[1]
        if source.lower() == "owid":
            crawl_owid(use_local)
        elif source.lower() == "phe":
            crawl_phe(use_local)
        elif source.lower() == "phs":
            crawl_phs(use_local)
        elif source.lower() == "phw":
            crawl_phw(use_local)
    else:
        crawl_owid(use_local)
        crawl_phe(use_local)
        crawl_phs(use_local)
        crawl_phw(use_local)
