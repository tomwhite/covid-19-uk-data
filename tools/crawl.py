#!/usr/bin/env python

from bs4 import BeautifulSoup
import dateparser
import datetime
from enum import Enum
import json
import math
import os
import pandas as pd
import re
import requests
import sqlite3
import sys
import xmltodict

from parsers import (
    parse_daily_areas,
    parse_daily_areas_json,
    parse_daily_areas_pdf,
    parse_totals,
    parse_totals_pdf,
    print_totals,
    save_indicators,
    save_indicators_to_sqlite,
    save_daily_areas,
    save_daily_areas_to_sqlite,
)
from util import format_country, normalize_int, normalize_whitespace

class DatasetUpdate(Enum):
    ALREADY_UPDATED = 1
    UPDATE_AVAILABLE = 2
    UPDATE_NOT_AVAILABLE = 3

def crawl(date, dataset, check_only=False):
    if dataset.lower() == "wales":
        return crawl_pdf(date, "Wales", check_only)
    elif dataset.lower() == "scotland":
        return crawl_html(date, "Scotland", check_only)
    elif dataset.lower() in ("ni", "northern ireland"):
        return crawl_pdf(date, "Northern Ireland", check_only)
    elif dataset.lower() == "uk":
        return crawl_html(date, "UK", check_only)
    elif dataset.lower() == "england":
        return crawl_arcgis(date, "England", check_only)
    elif dataset.lower() == "uk-daily-indicators":
        return crawl_arcgis(date, "UK", check_only)
    elif dataset.lower() == "uk-cases-and-deaths":
        return crawl_json(date, "UK", check_only)


def get_html_url(date, country):
    if country == "UK":
        return "https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public"
    elif country == "Scotland":
        return "https://www.gov.scot/publications/coronavirus-covid-19-tests-and-cases-in-scotland/"
    elif country == "Wales":
        # no longer used
        return "https://covid19-phwstatement.nhs.wales/"
    elif country == "Northern Ireland":
        # prior to 2020-03-24
        count = (dateparser.parse(date) - dateparser.parse("2020-03-08")).days
        return "https://www.health-ni.gov.uk/news/latest-update-coronavirus-covid-19-{}".format(count)

def crawl_html(date, country, check_only):
    html_url = get_html_url(date, country)
    local_html_file = "data/raw/coronavirus-covid-19-number-of-cases-in-{}-{}.html".format(
        format_country(country), date
    )
    save_html_file = False

    try:
        with open(local_html_file) as f:
            html = f.read()
        if check_only:
            return DatasetUpdate.ALREADY_UPDATED
    except FileNotFoundError:
        r = requests.get(html_url)
        html = r.text
        save_html_file = True

    results = parse_totals(country, html)

    if results is None:
        if check_only:
            return DatasetUpdate.UPDATE_AVAILABLE
        sys.stderr.write("Can't find numbers. Perhaps the page format has changed?\n")
        sys.exit(1)
    elif results["Date"] != date:
        if check_only:
            return DatasetUpdate.UPDATE_NOT_AVAILABLE
        sys.stderr.write("Page is dated {}, but want {}\n".format(results["Date"], date))
        sys.exit(1)

    if check_only:
        return DatasetUpdate.UPDATE_AVAILABLE

    daily_areas = parse_daily_areas(date, country, html)

    print_totals(results)
    #save_indicators(results)
    save_indicators_to_sqlite(results)

    if daily_areas is not None:
        #save_daily_areas(date, country, daily_areas)
        save_daily_areas_to_sqlite(date, country, daily_areas)

    if save_html_file:
        with open(local_html_file, "w") as f:
            f.write(html)


def get_json_url(date):
    # See https://github.com/PublicHealthEngland/coronavirus-dashboard
    blobs_url = "https://publicdashacc.blob.core.windows.net/publicdata?restype=container&comp=list"
    r = requests.get(blobs_url)
    blobs_xml = r.text
    blobs_dict = xmltodict.parse(blobs_xml)
    blob_names = sorted([o["Name"] for o in blobs_dict["EnumerationResults"]["Blobs"]["Blob"] if o["Name"]])
    dt = dateparser.parse(date, date_formats=['%Y-%m-%d'], locales=["en-GB"])
    blob_names_for_date = [name for name in blob_names if name.startswith("data_{}".format(dt.strftime('%Y%m%d')))]
    if len(blob_names_for_date) == 0:
        return None
    # Use most recent one
    return "https://c19pub.azureedge.net/{}".format(blob_names_for_date[-1])


def crawl_json(date, country, check_only):
    if country == "UK":
        local_data_file = "data/raw/phe/coronavirus-covid-19-number-of-cases-in-{}-{}.json".format(
            format_country(country), date
        )
        
        if not os.path.exists(local_data_file):
            data_url = get_json_url(date)

            if data_url is None:
                if check_only:
                    return DatasetUpdate.UPDATE_NOT_AVAILABLE
                sys.stderr.write("No data available for {}\n".format(date))
                sys.exit(1)         

            if check_only:
                return DatasetUpdate.UPDATE_AVAILABLE       

            r = requests.get(data_url)
            with open(local_data_file, "w") as f:
                f.write(r.text)

        if check_only:
            return DatasetUpdate.ALREADY_UPDATED

        with open(local_data_file) as f:
            json_data = json.load(f)

            totalUKCases = json_data["overview"]["K02000001"]["totalCases"]["value"]
            totalUKDeaths = json_data["overview"]["K02000001"]["deaths"]["value"]
            englandCases = json_data["countries"]["E92000001"]["totalCases"]["value"]
            englandDeaths = json_data["countries"]["E92000001"]["deaths"]["value"]

            with sqlite3.connect('data/covid-19-uk.db') as conn:
                c = conn.cursor()
                c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'UK', 'ConfirmedCases', {totalUKCases})")
                c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'UK', 'Deaths', {totalUKDeaths})")
                c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'England', 'ConfirmedCases', {englandCases})")
                c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'England', 'Deaths', {englandDeaths})")

            # get area data for England
            daily_areas = parse_daily_areas_json(date, "England", json_data)
            if daily_areas is not None:
                #save_daily_areas(date, "England", daily_areas)
                save_daily_areas_to_sqlite(date, "England", daily_areas)

def crawl_pdf(date, country, check_only):
    if country == "Northern Ireland":

        dt = dateparser.parse(date, date_formats=['%Y-%m-%d'], locales=["en-GB"])
        ym = dt.strftime('%Y-%m')
        dmy = dt.strftime('%d.%m.%y')
        # the top-level page containing links to PDFs
        html_url = "https://www.publichealth.hscni.net/publications/covid-19-surveillance-reports"
        # the PDF itself
        pdf_url = "https://www.publichealth.hscni.net/sites/default/files/{}/COVID-19 Surveillance Bulletin {}.pdf".format(ym, dmy)
        local_pdf_file = "data/raw/Daily_bulletin_DoH_{}.pdf".format(date)

        if not os.path.exists(local_pdf_file):
            r = requests.get(html_url)
            if "{}.pdf".format(dmy) not in r.text:
                if check_only:
                    return DatasetUpdate.UPDATE_NOT_AVAILABLE
                sys.stderr.write("Page is dated ?, but want {}\n".format(date))
                sys.exit(1)

            if check_only:
                return DatasetUpdate.UPDATE_AVAILABLE

            r = requests.get(pdf_url)
            with open(local_pdf_file, "wb") as f:
                f.write(r.content)

        if check_only:
            return DatasetUpdate.ALREADY_UPDATED

        results = parse_totals_pdf(date, country, local_pdf_file)

        if results is None:
            sys.stderr.write("Can't find numbers. Perhaps the page format has changed?\n")
            sys.exit(1)
        elif results["Date"] != date:
            sys.stderr.write("Page is dated {}, but want {}\n".format(results["Date"], date))
            sys.exit(1)

        print_totals(results)
        #save_indicators(results)
        save_indicators_to_sqlite(results)

        daily_areas = parse_daily_areas_pdf(date, country, local_pdf_file)
        if daily_areas is not None:
            #save_daily_areas(date, country, daily_areas)
            save_daily_areas_to_sqlite(date, country, daily_areas)

    elif country == "Wales":
        local_pdf_file = "data/raw/phw/LAs-{}.pdf".format(date)
        if not os.path.exists(local_pdf_file):
            if check_only:
                return DatasetUpdate.UPDATE_NOT_AVAILABLE
            sys.stderr.write("Page is dated ?, but want {}\n".format(date))
            sys.exit(1)

        if check_only:
            return DatasetUpdate.ALREADY_UPDATED

        daily_areas = parse_daily_areas_pdf(date, country, local_pdf_file)
        if daily_areas is not None:
            #save_daily_areas(date, country, daily_areas)
            save_daily_areas_to_sqlite(date, country, daily_areas)

        local_pdf_file = "data/raw/phw/HeadlineSummary-{}.pdf".format(date)

        if not os.path.exists(local_pdf_file):
            if check_only:
                return DatasetUpdate.UPDATE_NOT_AVAILABLE
            sys.stderr.write("Page is dated ?, but want {}\n".format(date))
            sys.exit(1)

        results = parse_totals_pdf(date, country, local_pdf_file)

        if results is None:
            sys.stderr.write("Can't find numbers. Perhaps the page format has changed?\n")
            sys.exit(1)
        elif results["Date"] != date:
            sys.stderr.write("Page is dated {}, but want {}\n".format(results["Date"], date))
            sys.exit(1)

        print_totals(results)
        #save_indicators(results)
        save_indicators_to_sqlite(results)


def download_arcgis_item(date, item_id, local_data_file, check_only):
    json_url = "https://www.arcgis.com/sharing/rest/content/items/{}?f=json".format(item_id)
    data_url = "https://www.arcgis.com/sharing/rest/content/items/{}/data".format(item_id)
    if not os.path.exists(local_data_file):
        r = requests.get(json_url)
        # https://developers.arcgis.com/rest/users-groups-and-items/item.htm
        item = json.loads(r.text)
        unixtimestamp = item['modified'] / 1000
        updated_date = datetime.datetime.fromtimestamp(unixtimestamp).strftime('%Y-%m-%d')

        if updated_date != date:
            if check_only:
                return DatasetUpdate.UPDATE_NOT_AVAILABLE
            sys.stderr.write("Page is dated {}, but want {}\n".format(updated_date, date))
            sys.exit(1)

        if check_only:
            return DatasetUpdate.UPDATE_AVAILABLE

        r = requests.get(data_url)

        with open(local_data_file, "wb") as f:
            f.write(r.content)
    if check_only:
        return DatasetUpdate.ALREADY_UPDATED

def crawl_arcgis(date, country, check_only):
    if country == "UK":
        item_id = "bc8ee90225644ef7a6f4dd1b13ea1d67"
        local_data_file = "data/raw/DailyIndicators-{}.xslx".format(date)
        ret = download_arcgis_item(date, item_id, local_data_file, check_only)
        if check_only:
            return ret

        df = pd.read_excel(local_data_file)
        print(df)

        d = df.to_dict("records")[0]
        date = d["DateVal"].strftime("%Y-%m-%d")

        with sqlite3.connect('data/covid-19-uk.db') as conn:
            c = conn.cursor()
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'UK', 'ConfirmedCases', {d['TotalUKCases']})")
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'UK', 'Deaths', {d['TotalUKDeaths']})")
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'England', 'ConfirmedCases', {d['EnglandCases']})")
            c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'England', 'Deaths', {d['EnglandDeaths']})")
            # c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'Scotland', 'ConfirmedCases', {d['ScotlandCases']})")
            # c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'Scotland', 'Deaths', {d['ScotlandDeaths']})")
            # c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'Wales', 'ConfirmedCases', {d['WalesCases']})")
            # c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'Wales', 'Deaths', {d['WalesDeaths']})")
            # c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'Northern Ireland', 'ConfirmedCases', {d['NICases']})")
            # c.execute(f"INSERT OR REPLACE INTO indicators VALUES ('{date}', 'Northern Ireland', 'Deaths', {d['NIDeaths']})")

    elif country == "England":
        item_id = "b684319181f94875a6879bbc833ca3a6"
        local_data_file = "data/raw/CountyUAs_cases_table-{}.csv".format(date)
        ret = download_arcgis_item(date, item_id, local_data_file, check_only)
        if check_only:
            return ret

        df = pd.read_csv(local_data_file)
        df["Date"] = date
        df["Country"] = "England"
        df = df.rename(columns={"GSS_CD": "AreaCode", "GSS_NM": "Area"})
        df = df[["Date", "Country", "AreaCode", "Area", "TotalCases"]]
        daily_areas = df.to_dict("split")["data"]
        for row in daily_areas:
            row[4] = normalize_int(normalize_whitespace(row[4]))
        daily_areas = [["Date", "Country", "AreaCode", "Area", "TotalCases"]] + daily_areas

        #save_daily_areas(date, country, daily_areas)
        save_daily_areas_to_sqlite(date, country, daily_areas)


if __name__ == "__main__":
    # TODO: default to today if no date passed in
    if len(sys.argv) == 1: # check for updates
        now = datetime.datetime.now()
        if now.hour < 14:
            print("There are no updates before 14:00")
            sys.exit(0)
        date = now.strftime('%Y-%m-%d')
        datasets = ["Wales", "UK"]
        new_updates_available = False
        for dataset in datasets:
            updated = crawl(date, dataset, check_only=True)
            if updated is DatasetUpdate.UPDATE_AVAILABLE:
                print("Update available for {} {}!".format(date, dataset))
                new_updates_available = True
            elif updated is DatasetUpdate.UPDATE_NOT_AVAILABLE:
                print("No update available for {} {}".format(date, dataset))
            elif updated is DatasetUpdate.ALREADY_UPDATED:
                print("Already updated for {} {}".format(date, dataset))
        sys.exit(1 if new_updates_available else 0) # non zero if any new updates for watch(1)
    else:
        date = sys.argv[1]
        dataset = sys.argv[2]
        crawl(date, dataset)
