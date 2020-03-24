#!/usr/bin/env python

from bs4 import BeautifulSoup
import dateparser
import datetime
import json
import math
import os
import pandas as pd
import re
import requests
import sqlite3
import sys

from parsers import (
    parse_daily_areas,
    parse_totals,
    print_totals,
    scotland_pattern,
    save_indicators,
    save_indicators_to_sqlite,
    save_daily_areas,
    save_daily_areas_to_sqlite,
)
from util import format_country, normalize_int, normalize_whitespace


def crawl(date, dataset):
    if dataset.lower() == "wales":
        crawl_html(date, "Wales")
    elif dataset.lower() == "scotland":
        crawl_html(date, "Scotland")
    elif dataset.lower() in ("ni", "northern ireland"):
        crawl_html(date, "Northern Ireland")
    elif dataset.lower() == "uk":
        crawl_html(date, "UK")
    elif dataset.lower() == "england":
        crawl_arcgis(date, "England")
    elif dataset.lower() == "uk-daily-indicators":
        crawl_arcgis(date, "UK")


def get_html_url(date, country):
    if country == "UK":
        return "https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public"
    elif country == "Scotland":
        return "https://www.gov.scot/coronavirus-covid-19/"
    elif country == "Wales":
        return "https://covid19-phwstatement.nhs.wales/"
    elif country == "Northern Ireland":
        count = (dateparser.parse(date) - dateparser.parse("2020-03-08")).days
        return "https://www.health-ni.gov.uk/news/latest-update-coronavirus-covid-19-{}".format(count)

def crawl_html(date, country):
    html_url = get_html_url(date, country)
    local_html_file = "data/raw/coronavirus-covid-19-number-of-cases-in-{}-{}.html".format(
        format_country(country), date
    )
    save_html_file = False

    try:
        with open(local_html_file) as f:
            html = f.read()
    except FileNotFoundError:
        r = requests.get(html_url)
        html = r.text
        save_html_file = True

    results = parse_totals(country, html)

    if results is None:
        sys.stderr.write("Can't find numbers. Perhaps the page format has changed?\n")
        sys.exit(1)
    elif results["Date"] != date:
        sys.stderr.write("Page is dated {}, but want {}\n".format(results["Date"], date))
        sys.exit(1)

    daily_areas = parse_daily_areas(date, country, html)

    print_totals(results)
    #save_indicators(results)
    save_indicators_to_sqlite(results)

    if daily_areas is not None:
        save_daily_areas(date, country, daily_areas)
        save_daily_areas_to_sqlite(date, country, daily_areas)

    if save_html_file:
        with open(local_html_file, "w") as f:
            f.write(html)


def download_arcgis_item(date, item_id, local_data_file):
    json_url = "https://www.arcgis.com/sharing/rest/content/items/{}?f=json".format(item_id)
    data_url = "https://www.arcgis.com/sharing/rest/content/items/{}/data".format(item_id)
    if not os.path.exists(local_data_file):
        r = requests.get(json_url)
        # https://developers.arcgis.com/rest/users-groups-and-items/item.htm
        item = json.loads(r.text)
        unixtimestamp = item['modified'] / 1000
        updated_date = datetime.datetime.fromtimestamp(unixtimestamp).strftime('%Y-%m-%d')

        if updated_date != date:
            sys.stderr.write("Page is dated {}, but want {}\n".format(updated_date, date))
            sys.exit(1)

        r = requests.get(data_url)

        with open(local_data_file, "wb") as f:
            f.write(r.content)

def crawl_arcgis(date, country):
    if country == "UK":
        item_id = "bc8ee90225644ef7a6f4dd1b13ea1d67"
        local_data_file = "data/raw/DailyIndicators-{}.xslx".format(date)
        download_arcgis_item(date, item_id, local_data_file)

        df = pd.read_excel(local_data_file)
        print(df)

        d = df.to_dict("records")[0]
        date = d["DateVal"].strftime("%Y-%m-%d")

        with sqlite3.connect('data/covid-19-uk.db') as conn:
            c = conn.cursor()
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'UK', 'ConfirmedCases', {d['TotalUKCases']})")
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'UK', 'Deaths', {d['TotalUKDeaths']})")
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'England', 'ConfirmedCases', {d['EnglandCases']})")
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'Scotland', 'ConfirmedCases', {d['ScotlandCases']})")
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'Wales', 'ConfirmedCases', {d['WalesCases']})")
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'Northern Ireland', 'ConfirmedCases', {d['NICases']})")

    elif country == "England":
        item_id = "b684319181f94875a6879bbc833ca3a6"
        local_data_file = "data/raw/CountyUAs_cases_table-{}.csv".format(date)
        download_arcgis_item(date, item_id, local_data_file)

        df = pd.read_csv(local_data_file)
        df["Date"] = date
        df["Country"] = "England"
        df = df.rename(columns={"GSS_CD": "AreaCode", "GSS_NM": "Area"})
        df = df[["Date", "Country", "AreaCode", "Area", "TotalCases"]]
        daily_areas = df.to_dict("split")["data"]
        daily_areas = [["Date", "Country", "AreaCode", "Area", "TotalCases"]] + daily_areas

        save_daily_areas(date, country, daily_areas)
        save_daily_areas_to_sqlite(date, country, daily_areas)


if __name__ == "__main__":
    # TODO: default to today if no date passed in
    date = sys.argv[1]
    dataset = sys.argv[2]
    crawl(date, dataset)
