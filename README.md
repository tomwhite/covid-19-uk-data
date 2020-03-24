# COVID-19 UK Historical Data

Data on testing and case numbers for coronavirus (COVID-19) in the UK is published by the government, but it is fragmented and not always provided in consistent or machine-friendly formats. Also, in many cases only the latest numbers are available so it's not possible to look at changes over time.

This site collates the historical data and provides it in an easily consumable format (CSV), in both wide and [tidy data](https://en.wikipedia.org/wiki/Tidy_data) forms.

Ideally the data publishers will start doing this so this site becomes redundant.

## Data files

The following CSV files are available:

* [data/covid-19-cases-uk.csv](data/covid-19-cases-uk.csv): daily counts of confirmed cases for (upper tier) local authorities in England, and health boards in Scotland and Wales. No data for Northern Ireland is currently available.
    * Note that prior to 18 March 2020 Wales data was broken down by local authority, not heath board.
* [data/covid-19-totals-uk.csv](data/covid-19-totals-uk.csv): daily counts of tests, confirmed cases, deaths for the whole of the UK
* [data/covid-19-totals-england.csv](data/covid-19-totals-england.csv): daily counts of tests, confirmed cases, deaths for England
* [data/covid-19-totals-northern-ireland.csv](data/covid-19-totals-northern-ireland.csv): daily counts of tests, confirmed cases, deaths for Northern Ireland
* [data/covid-19-totals-scotland.csv](data/covid-19-totals-scotland.csv): daily counts of tests, confirmed cases, deaths for Scotland
* [data/covid-19-totals-wales.csv](data/covid-19-totals-wales.csv): daily counts of tests, confirmed cases, deaths for Wales
* [data/covid-19-indicators-uk.csv](data/covid-19-indicators-uk.csv): daily counts of tests, confirmed cases, deaths for the whole of the UK and individual countries in the UK (England, Scotland, Wales, Northern Ireland). This is a tidy-data version of _covid-19-totals-*.csv_ combined into one file.
* _data/daily/*.csv_: daily counts, with a separate file for each date and country.

You can use these files without reading the rest of this document.

## News

* 21 March 2020. PHW is back to health board (not LA) breakdowns again, this time it looks permanent.
* 20 March 2020. PHW is providing LA area breakdowns again, after not doing so for two days.
* 18 March 2020. PHW is no longer providing LA area breakdowns. "Novel Coronavirus (COVID-19) is now circulating in every part of Wales. For this reason, we will not be reporting cases by local authority area from today. From tomorrow, we will update daily at 12 noon the case numbers by health board of residence."

## Wishlist

Here are my suggestions for how to improve the data being published by public bodies.

The short version: **publish everything in CSV format, and include historical data!**

Department of Health and Social Care, and Public Health England
1. Publish historical data, not just the current day's data.
2. Add a column for number of recovered patients to the [daily indicators](https://www.arcgis.com/home/item.html?id=bc8ee90225644ef7a6f4dd1b13ea1d67). (It is published on the dashboard, but nowhere else.)
3. Publish deaths by hospital every day.

Public Health Wales
1. Publish the number of tests being performed every day.
2. Publish daily totals (tests, confirmed cases, deaths) in machine readable form (CSV). Or failing that, at least in a consistent format on a web page.
3. Publish confirmed cases by local authority/health board in machine readable form (CSV).
4. Publish historical data, not just the current day's data.
5. Publish deaths by hospital every day.

Public Health Scotland
1. Publish daily totals (tests, confirmed cases, deaths) in machine readable form (CSV).
2. Publish confirmed cases by local authority/health board in machine readable form (CSV).
3. Publish historical data, not just the current day's data.
4. Publish deaths by hospital every day.

Public Health Northern Ireland
1. Publish daily totals (tests, confirmed cases, deaths) in machine readable form (CSV).
2. Publish confirmed cases by local authority/health board in machine readable form (CSV). These are not currently being published, so it would be good to be able to get these figures, even if just on a web page.
3. Publish historical data, not just the current day's data.
4. Publish deaths by hospital every day.

## Data sources and the collation process

A lot of the collation process is manual, however there are a few command line tools to help process the data into its final form. The data sources are changing from day to day, which means the process is constantly changing.

Raw data is archived under _data/raw_, it should never be edited.

### UK

* Number of **tests** and **confirmed cases** are published at [https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public#number-of-cases](https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public#number-of-cases) at 2pm in HTML format
* Number of **deaths** are published in the [daily indicators](https://www.arcgis.com/home/item.html?id=bc8ee90225644ef7a6f4dd1b13ea1d67) at 6pm in XLSX format
* Twitter updates: [@DHSCgovuk](https://twitter.com/DHSCgovuk)

### England

* Number of **tests** are not published
* Number of **confirmed cases** are published in the [daily indicators](https://www.arcgis.com/home/item.html?id=bc8ee90225644ef7a6f4dd1b13ea1d67) at 6pm in XLSX format
* Number of **deaths** are not published
* Number of **confirmed cases by local authority** are published in the [UTLA cases table](https://www.arcgis.com/home/item.html?id=b684319181f94875a6879bbc833ca3a6) at 6pm in CSV format
    * Note that prior to 11 March 2020 case numbers were published in HTML format.

### Scotland

* Number of **tests, confirmed cases and deaths**, and **confirmed cases by local authority**, are published at [www.gov.scot/coronavirus-covid-19](https://www.gov.scot/coronavirus-covid-19/) at 2pm in HTML format

### Wales

* Number of **tests** are not published
* Number of **confirmed cases and deaths**, and **confirmed cases by local authority**, are published at [https://covid19-phwstatement.nhs.wales/](https://covid19-phwstatement.nhs.wales/) at midday in HTML format
* Number of **confirmed cases by local authority** are published in the [UTLA cases table](https://www.arcgis.com/home/item.html?id=b684319181f94875a6879bbc833ca3a6)
    * Note that prior to 11 March 2020 case numbers were published in HTML format.
* Twitter updates: [@PublicHealthW](https://twitter.com/publichealthw)

### Northern Ireland

* Number of **tests, confirmed cases and deaths** are published at [https://www.health-ni.gov.uk/news/](https://www.health-ni.gov.uk/news/) at 2pm in HTML format (on a new page each day)
* Number of **confirmed cases by local authority** are not published
* Twitter updates: [@publichealthni](https://twitter.com/publichealthni)

Note that [daily indicators](https://www.arcgis.com/home/item.html?id=bc8ee90225644ef7a6f4dd1b13ea1d67) includes confirmed cases for all countries.

### By URL

|URL|What|When|Format|Archived?|
|---|----|----|------|---------|
|https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public|UK tests, UK confirmed cases|2pm|HTML|Yes|
|https://www.arcgis.com/sharing/rest/content/items/bc8ee90225644ef7a6f4dd1b13ea1d67/data|UK tests, England/Scotland/Wales/NI confirmed cases, UK deaths ("daily indicators")|6pm|XLSX|No|
|https://www.arcgis.com/sharing/rest/content/items/b684319181f94875a6879bbc833ca3a6/data|England confirmed cases by local authority ("UTLA cases table")|6pm|CSV|No|
|https://www.arcgis.com/sharing/rest/content/items/ca796627a2294c51926865748c4a56e8/data|England confirmed cases by NHS region ("NHA regional cases table")|6pm|CSV|No|
|https://www.gov.scot/coronavirus-covid-19/|Scotland tests, confirmed cases, deaths, confirmed cases by local authority|2pm|HTML|Yes|
|https://covid19-phwstatement.nhs.wales/|Wales confirmed cases, deaths, confirmed cases by local authority|midday|HTML|Yes|
|https://www.health-ni.gov.uk/news/|Northern Ireland tests, confirmed cases, deaths|2pm|HTML|No|

Note that the arcgis.com links are direct links to the data.

### Local Authority and Health Board metadata

* English and Welsh local authorities: [Lower Tier Local Authority to Upper Tier Local Authority (April 2019) Lookup in England and Wales](http://geoportal1-ons.opendata.arcgis.com/datasets/lower-tier-local-authority-to-upper-tier-local-authority-april-2019-lookup-in-england-and-wales/data)
* Scottish Health Boards: [Health Board 2014](https://www.opendata.nhs.scot/dataset/geography-codes-and-labels/resource/652ff726-e676-4a20-abda-435b98dd7bdc)
* Welsh Health Boards: [Local Health Boards (April 2019) Names and Codes in Wales](https://geoportal.statistics.gov.uk/datasets/local-health-boards-april-2019-names-and-codes-in-wales)

## Related projects

* Ian Watt's [COVID-19 Scotland dataset](https://github.com/watty62/Scot_covid19)
* Emma Dought's [UK COVID-19 data](https://github.com/emmadoughty/Daily_COVID-19)

## Tools

There are command line tools for downloading, parsing, and processing the data. They rely on Python 3.

To install the tools, create a virtual environment, activate it, then install the required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Daily workflow

A sqlite DB is now used to store and aggregate intermediate data. The CSV files remain the point of record.

The **crawl** tool will see if the reseouce (webpage, date file) has already been downloaded, and if it hasn't download it if it's available for the specified date (today). (If not available the tool will exit.) If available, the tool will then extract the relevant information from it and update the sqlite database. This means that you can just run **crawl** until it finds new updates.

The **convert_sqlite_to_csvs** tool will extract the data from sqlite and update the CSV files.

```bash
DATE=$(date +'%Y-%m-%d')
./tools/crawl.py $DATE Wales
./tools/convert_sqlite_to_csvs.py
git add data; git commit -am "Update for $DATE for Wales"
```

```bash
DATE=$(date +'%Y-%m-%d')
./tools/crawl.py $DATE Scotland
./tools/convert_sqlite_to_csvs.py
git add data; git commit -am "Update for $DATE for Scotland"
```

```bash
DATE=$(date +'%Y-%m-%d')
./tools/crawl.py $DATE 'Northern Ireland'
./tools/convert_sqlite_to_csvs.py
git add data; git commit -am "Update for $DATE for Northern Ireland"
```

```bash
DATE=$(date +'%Y-%m-%d')
./tools/crawl.py $DATE UK
./tools/convert_sqlite_to_csvs.py
git add data; git commit -am "Update for $DATE for UK"
```

```bash
DATE=$(date +'%Y-%m-%d')
./tools/crawl.py $DATE UK-daily-indicators
./tools/convert_sqlite_to_csvs.py
git add data; git commit -am "Update for $DATE for UK daily indicators"
```

```bash
DATE=$(date +'%Y-%m-%d')
./tools/crawl.py $DATE England
./tools/convert_sqlite_to_csvs.py
git add data; git commit -am "Update for $DATE for England"
```

Check data consistency
```bash
./tools/check_indicators.py
./tools/check_totals.py
```

### Manual overrides

Sometimes it's necessary to fix data by hand. In this case the following tools are useful:

Repopulate the sqlite database from the CSV files:
```bash
rm data/covid-19-uk.db
csvs-to-sqlite --replace-tables -t indicators -pk Date -pk Country -pk Indicator data/covid-19-indicators-uk.csv data/covid-19-uk.db
csvs-to-sqlite --replace-tables -t cases -pk Date -pk Country -pk AreaCode -pk Area data/covid-19-cases-uk.csv data/covid-19-uk.db
```

## Daily workflow (obsolete)

England (2pm, with area totals an hour or two later):

### Make commands

1. `make england-all`: Runs all of the `UA Daily` and `Totals` commands listed below in a single master command

#### UA Daily

1. `make england-ua-dailies`: Runs all of the commands below
1. `make england-ua-dailies-download`: Download the daily UAs
1. `make england-ua-dailies-generate`: Generate the daily UAs (requires `make england-ua-dailies-generate` to be run first)

#### Totals

1. `make england-totals`: Runs all of the commands below
1. `make england-totals-download`: Download a temp HTML file containing the totals
1. `make england-totals-generate`: Generate the totals from the temp HTML file (requires `make england-totals-download` to be run first) will append to the `./data/covid-19-totals-uk.csv` if the temp HTML file contains today's date
1. `make england-totals-cleanup`: Removed the temp HTML file (requires `make england-totals-download` to be run first)

### Manually running scripts

Wales (11am)

```bash
DATE=$(date +'%Y-%m-%d')
curl -L https://covid19-phwstatement.nhs.wales/ -o data/raw/coronavirus-covid-19-number-of-cases-in-wales-$DATE.html
./tools/gen_daily_areas_wales.py data/raw/coronavirus-covid-19-number-of-cases-in-wales-$DATE.html data/daily/covid-19-cases-$DATE-wales.csv
# Edit data/covid-19-totals-wales.csv (only have test numbers on Thursdays, leave column blank on other days)
./tools/extract_totals.py data/raw/coronavirus-covid-19-number-of-cases-in-wales-$DATE.html
```

Scotland (2pm)

```bash
DATE=$(date +'%Y-%m-%d')
curl -L https://www.gov.scot/coronavirus-covid-19/ -o data/raw/coronavirus-covid-19-number-of-cases-in-scotland-$DATE.html
./tools/gen_daily_areas_scotland.py data/raw/coronavirus-covid-19-number-of-cases-in-scotland-$DATE.html data/daily/covid-19-cases-$DATE-scotland.csv
# Edit data/covid-19-totals-scotland.csv with output from running the following (double check numbers)
./tools/extract_totals.py data/raw/coronavirus-covid-19-number-of-cases-in-scotland-$DATE.html
```

England (2pm):

```bash
DATE=$(date +'%Y-%m-%d')
# Edit data/covid-19-totals-uk.csv with output from running the following (double check numbers)
curl -L https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public -o data/raw/coronavirus-covid-19-number-of-cases-in-uk-$DATE.html
./tools/extract_totals.py data/raw/coronavirus-covid-19-number-of-cases-in-uk-$DATE.html
```

England (6pm):

```bash
DATE=$(date +'%Y-%m-%d')
curl -L https://www.arcgis.com/sharing/rest/content/items/b684319181f94875a6879bbc833ca3a6/data -o data/raw/CountyUAs_cases_table-$DATE.csv
curl -L https://www.arcgis.com/sharing/rest/content/items/ca796627a2294c51926865748c4a56e8/data -o data/raw/NHSR_Cases_table-$DATE.csv
./tools/gen_daily_areas_england.py data/raw/CountyUAs_cases_table-$DATE.csv data/daily/covid-19-cases-$DATE-england.csv
# Edit data/covid-19-totals-uk.csv with output from running the following (double check numbers)
# Also edit data/covid-19-indicators.csv
curl -L https://www.arcgis.com/sharing/rest/content/items/bc8ee90225644ef7a6f4dd1b13ea1d67/data -o data/raw/DailyIndicators-$DATE.xslx
./tools/extract_indicators.py data/raw/DailyIndicators-$DATE.xslx
```

Northern Ireland (2pm)

* Get test numbers from [https://www.health-ni.gov.uk/news/][https://www.health-ni.gov.uk/news/]

Northern Ireland (evening)

_This is often no longer needed since the numbers come from the daily indicators_

```bash
open https://www.publichealth.hscni.net/news/covid-19-coronavirus#situation-in-northern-ireland
# Edit data/covid-19-totals-northern-ireland.csv with output from running the following (double check numbers)
curl -L https://www.publichealth.hscni.net/news/covid-19-coronavirus -o ni-tmp.html
./tools/extract_totals.py ni-tmp.html
```

Consolidate and check

```bash
./tools/consolidate_daily_areas.py
./tools/convert_totals_to_indicators.py
./tools/check_indicators.py
./tools/check_totals.py
```
