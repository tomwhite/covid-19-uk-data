# COVID-19 UK Historical Data

Data on testing and case numbers for coronavirus (COVID-19) in the UK is published by the government, but it is fragmented and not always provided in consistent or machine-friendly formats. Also, in many cases only the latest numbers are available so it's not possible to look at changes over time.

This site collates the historical data and provides it in an easily consumable format (CSV), in [tidy data](https://en.wikipedia.org/wiki/Tidy_data) form.

Ideally the data publishers will start doing this so this site becomes redundant.

## Data files

The following CSV files are available:

* [data/covid-19-cases-uk.csv](data/covid-19-cases-uk.csv): daily counts of confirmed cases for (upper tier) local authorities in England and Wales, and health boards in Scotland. No data for Northern Ireland is currently available.
* [data/covid-19-indicators-uk.csv](data/covid-19-indicators-uk.csv): daily counts of tests, confirmed cases, deaths for the whole of the UK and individual countries in the UK (England, Scotland, Wales, Northern Ireland)
* _data/daily/*.csv_: daily counts, with a separate file for each date and country.

You can use these files without reading the rest of this document.

The following CSV files are deprecated, please use [data/covid-19-indicators-uk.csv](data/covid-19-indicators-uk.csv) instead:

* [data/covid-19-totals-uk.csv](data/covid-19-totals-uk.csv): daily counts of tests, confirmed cases, deaths for the whole of the UK
* [data/covid-19-totals-northern-ireland.csv](data/covid-19-totals-northern-ireland.csv): daily counts of tests, confirmed cases, deaths for Northern Ireland
* [data/covid-19-totals-scotland.csv](data/covid-19-totals-scotland.csv): daily counts of tests, confirmed cases, deaths for Scotland
* [data/covid-19-totals-wales.csv](data/covid-19-totals-wales.csv): daily counts of tests, confirmed cases, deaths for Wales

## News

* 18 March 2020. PHW is no longer providing LA area breakdowns. "Novel Coronavirus (COVID-19) is now circulating in every part of Wales. For this reason, we will not be reporting cases by local authority area from today. From tomorrow, we will update daily at 12 noon the case numbers by health board of residence."

## Data sources and the collation process

A lot of the collation process is manual, however there are a few command line tools to help process the data into its final form. The data sources are changing from day to day, which means the process is constantly changing.


### Local Authority and Health Board data

* English and Welsh local authorities: [Lower Tier Local Authority to Upper Tier Local Authority (April 2019) Lookup in England and Wales](http://geoportal1-ons.opendata.arcgis.com/datasets/lower-tier-local-authority-to-upper-tier-local-authority-april-2019-lookup-in-england-and-wales/data)
* Scottish Health Boards: [Health Board 2014](https://www.opendata.nhs.scot/dataset/geography-codes-and-labels/resource/652ff726-e676-4a20-abda-435b98dd7bdc)
* Welsh Health Boards: [Local Health Boards (April 2019) Names and Codes in Wales](https://geoportal.statistics.gov.uk/datasets/local-health-boards-april-2019-names-and-codes-in-wales)

### UK

* Number of **tests** and **confirmed cases** are published at [www.gov.uk/government/publications/covid-19-track-coronavirus-cases](https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases) at 2pm in HTML format
* Number of **deaths** are published in the [daily indicators](https://www.arcgis.com/home/item.html?id=bc8ee90225644ef7a6f4dd1b13ea1d67) at 6pm in XLSX format

### England

* Number of **tests** are not published
* Number of **confirmed cases** are published in the [daily indicators](https://www.arcgis.com/home/item.html?id=bc8ee90225644ef7a6f4dd1b13ea1d67) at 6pm in XLSX format
* Number of **deaths** are not published
* Number of **confirmed cases by local authority** are published in the [UTLA cases table](https://www.arcgis.com/home/item.html?id=b684319181f94875a6879bbc833ca3a6)
    * Note that prior to 11 March 2020 case numbers were published in HTML format.

### Scotland

* Number of **tests, confirmed cases and deaths**, and **confirmed cases by local authority**, are published at [www.gov.scot/coronavirus-covid-19](https://www.gov.scot/coronavirus-covid-19/) at 2pm in HTML format

### Wales

* Number of **tests** are not published
* Number of **confirmed cases and deaths**, and **confirmed cases by local authority**, are published at [phw.nhs.wales/news/public-health-wales-statement-on-novel-coronavirus-outbreak/](https://phw.nhs.wales/news/public-health-wales-statement-on-novel-coronavirus-outbreak/) at 11am in HTML format
* Number of **confirmed cases by local authority** are published in the [UTLA cases table](https://www.arcgis.com/home/item.html?id=b684319181f94875a6879bbc833ca3a6)
    * Note that prior to 11 March 2020 case numbers were published in HTML format.

### Northern Ireland

* Number of **tests** are not published
* Number of **confirmed cases** are published at [www.publichealth.hscni.net/news/covid-19-coronavirus](https://www.publichealth.hscni.net/news/covid-19-coronavirus) in the evening in HTML format
* Number of **deaths** are not published
* Number of **confirmed cases by local authority** are not published
* Twitter updates: [https://twitter.com/publichealthni](https://twitter.com/publichealthni)

Note that [daily indicators](https://www.arcgis.com/home/item.html?id=bc8ee90225644ef7a6f4dd1b13ea1d67) includes confirmed cases for all countries.

## Tools

The command line tools rely on Python 3.

Create a virtual environment, activate it, then install the required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The following shows some illustrative commands.

Convert case numbers for England:

```bash
./tools/gen_daily_areas_england.py data/raw/CountyUAs_cases_table-2020-03-11.csv data/daily/covid-19-cases-2020-03-11-england.csv
```

Convert case numbers for England prior to 11 March 2020 (note that the `gen_daily_areas_scotland.py` tool is used since the HTML pages have the same format):

```bash
./tools/gen_daily_areas_scotland.py data/raw/coronavirus-covid-19-number-of-cases-in-england-2020-03-05.html data/daily/covid-19-cases-2020-03-05-england.csv
./tools/gen_daily_areas_scotland.py data/raw/coronavirus-covid-19-number-of-cases-in-england-2020-03-07.html data/daily/covid-19-cases-2020-03-07-england.csv
./tools/gen_daily_areas_scotland.py data/raw/coronavirus-covid-19-number-of-cases-in-england-2020-03-08.html data/daily/covid-19-cases-2020-03-08-england.csv
./tools/gen_daily_areas_scotland.py data/raw/coronavirus-covid-19-number-of-cases-in-england-2020-03-09.html data/daily/covid-19-cases-2020-03-09-england.csv
./tools/gen_daily_areas_scotland.py data/raw/coronavirus-covid-19-number-of-cases-in-england-2020-03-10.html data/daily/covid-19-cases-2020-03-10-england.csv
```

Convert case numbers for Scotland:

```bash
./tools/gen_daily_areas_scotland.py data/raw/coronavirus-covid-19-number-of-cases-in-scotland-2020-03-12.html data/daily/covid-19-cases-2020-03-12-scotland.csv
```

Create a single consolidated CSV with all case numbers in it:

```bash
./tools/consolidate_daily_areas.py
```

Run a sanity check that the area case numbers add up to the totals:

```bash
./tools/check_totals.py
```



## Daily workflow

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
curl -L https://phw.nhs.wales/news/public-health-wales-statement-on-novel-coronavirus-outbreak/ -o data/raw/coronavirus-covid-19-number-of-cases-in-wales-$DATE.html
./tools/gen_daily_areas_wales.py data/raw/coronavirus-covid-19-number-of-cases-in-wales-$DATE.html data/daily/covid-19-cases-$DATE-wales.csv
# Edit data/covid-19-totals-wales.csv (only have test numbers on Thursdays, leave column blank on other days)
# Also edit data/covid-19-indicators.csv
./tools/extract_totals.py data/raw/coronavirus-covid-19-number-of-cases-in-wales-$DATE.html
```

Scotland (2pm)

```bash
DATE=$(date +'%Y-%m-%d')
curl -L https://www.gov.scot/coronavirus-covid-19/ -o data/raw/coronavirus-covid-19-number-of-cases-in-scotland-$DATE.html
./tools/gen_daily_areas_scotland.py data/raw/coronavirus-covid-19-number-of-cases-in-scotland-$DATE.html data/daily/covid-19-cases-$DATE-scotland.csv
# Edit data/covid-19-totals-scotland.csv with output from running the following (double check numbers)
# Also edit data/covid-19-indicators.csv
./tools/extract_totals.py data/raw/coronavirus-covid-19-number-of-cases-in-scotland-$DATE.html
```

England (2pm):

```bash
DATE=$(date +'%Y-%m-%d')
# Edit data/covid-19-totals-uk.csv with output from running the following (double check numbers)
# Also edit data/covid-19-indicators.csv
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
./tools/sort_indicators.py
./tools/check_totals.py
```
