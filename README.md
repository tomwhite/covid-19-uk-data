# COVID-19 UK Historical Data

Data on testing and case numbers for coronavirus (COVID-19) in the UK is published by the government, but it is fragmented and not always provided in consistent or machine-friendly formats. Also, in many cases only the latest numbers are available so it's not possible to look at changes over time.

This site collates the historical data and provides it in an easily consumable format (CSV), in [tidy data](https://en.wikipedia.org/wiki/Tidy_data) form.

Ideally the data publishers will start doing this so this site becomes redundant.

## Data files

The following CSV files are available:

* [data/covid-19-totals-uk.csv](data/covid-19-totals-uk.csv): daily counts of tests, confirmed cases, deaths for the whole of the UK
* [data/covid-19-totals-northern-ireland.csv](data/covid-19-totals-northern-ireland.csv): daily counts of tests, confirmed cases, deaths for Northern Ireland
* [data/covid-19-totals-scotland.csv](data/covid-19-totals-scotland.csv): daily counts of tests, confirmed cases, deaths for Scotland
* [data/covid-19-totals-wales.csv](data/covid-19-totals-wales.csv): daily counts of tests, confirmed cases, deaths for Wales
* [data/covid-19-cases-uk.csv](data/covid-19-cases-uk.csv): daily counts of confirmed cases for (upper tier) local authorities in England and Wales, and health boards in Scotland. No data for Northern Ireland is currently available.
* _data/daily/*.csv_: daily counts, with a separate file for each date and country.

You can use these files without reading the rest of this document.

## Data sources and the collation process

A lot of the collation process is manual, however there are a few command line tools to help process the data into its final form.

### Local Authority data

The following dataset is used to map between (upper tier) local authority names and codes : [Lower Tier Local Authority to Upper Tier Local Authority (April 2019) Lookup in England and Wales](http://geoportal1-ons.opendata.arcgis.com/datasets/lower-tier-local-authority-to-upper-tier-local-authority-april-2019-lookup-in-england-and-wales/data)

### England

Updates are published daily at [www.gov.uk/government/publications/covid-19-track-coronavirus-cases](https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases).

* Test numbers are published daily on Twitter by [https://twitter.com/DHSCgovuk](twitter.com/DHSCgovuk). The count is added to _data/covid-19-totals-uk.csv_ manually. Note that there isn't a separate breakdown of the England numbers - they cover the whole of the UK.
* Case numbers by local authority are published daily in the [UTLA cases table](https://www.arcgis.com/home/item.html?id=b684319181f94875a6879bbc833ca3a6), updating previous updates. There is no way to get historical data from this source (as far I can tell). The CSV file from this page is saved in _data/raw_.
  * Note that prior to 11 March 2020 case numbers were published in HTML format.

### Wales

Updates are published daily at [phw.nhs.wales/news/public-health-wales-statement-on-novel-coronavirus-outbreak/](https://phw.nhs.wales/news/public-health-wales-statement-on-novel-coronavirus-outbreak/), overwriting previous updates. (Note however that this page is being archived by [web.archive.org/](https://web.archive.org/)) Prior to 12 March 2020 updates were published at [gov.wales/announcements](https://gov.wales/announcements).

* Test numbers are published _weekly_ on Thursday. The count is added to _data/covid-19-totals-wales.csv_ manually.
  * Improvement: automatically download this page every Thursday
* Case numbers by local authority are published daily in prose form. They are manually added to _data/raw/wales-new-cases.csv_.

### Scotland

Updates are published daily at [www.gov.scot/coronavirus-covid-19](https://www.gov.scot/coronavirus-covid-19/), overwriting previous updates. (Note however that this page is being archived by [web.archive.org](https://web.archive.org/)).

* Test numbers are published daily and added to _data/covid-19-totals-scotland.csv_ manually.
* Case numbers by health board are published daily. The HTML file is save in _data/raw_.

### Northern Ireland

Updates are published daily at [www.publichealth.hscni.net/news/covid-19-coronavirus](https://www.publichealth.hscni.net/news/covid-19-coronavirus) and [https://twitter.com/publichealthni](twitter.com/publichealthni).

* Test numbers are published daily and added to _data/covid-19-totals-northern-ireland.csv_ manually.
* Case numbers by local authority are not available.

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

1. `make england-ua-dailies`: Runs all of the commands below
1. `make england-totals-download`: Download a temp HTML file containing the totals
1. `make england-totals-generate`: Generate the totals from the temp HTML file (requires `make england-totals-download` to be run first) will append to the `./data/covid-19-totals-uk.csv` if the temp HTML file contains today's date
1. `make england-totals-cleanup`: Removed the temp HTML file (requires `make england-totals-download` to be run first)

### Manually running scripts

```bash
DATE=$(date +'%Y-%m-%d')
open https://www.arcgis.com/home/item.html?id=b684319181f94875a6879bbc833ca3a6/data
mv ~/Downloads/CountyUAs_cases_table.csv data/raw/CountyUAs_cases_table-$DATE.csv
./tools/gen_daily_areas_england.py data/raw/CountyUAs_cases_table-$DATE.csv data/daily/covid-19-cases-$DATE-england.csv
open https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public#number-of-cases
# Edit data/covid-19-totals-uk.csv with output from running the following (double check numbers)
curl https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public -o uk-tmp.html
./tools/extract_totals.py uk-tmp.html
```

Wales (11am)

```bash
DATE=$(date +'%Y-%m-%d')
curl https://phw.nhs.wales/news/public-health-wales-statement-on-novel-coronavirus-outbreak/ -o data/raw/coronavirus-covid-19-number-of-cases-in-wales-$DATE.html
./tools/gen_daily_areas_wales.py data/raw/coronavirus-covid-19-number-of-cases-in-wales-$DATE.html data/daily/covid-19-cases-$DATE-wales.csv
# Edit data/covid-19-totals-wales.csv (only have test numbers on Thursdays, leave column blank on other days)
./tools/extract_totals.py data/raw/coronavirus-covid-19-number-of-cases-in-wales-$DATE.html
```

Scotland (2pm)

```bash
DATE=$(date +'%Y-%m-%d')
curl https://www.gov.scot/coronavirus-covid-19/ -o data/raw/coronavirus-covid-19-number-of-cases-in-scotland-$DATE.html
./tools/gen_daily_areas_scotland.py data/raw/coronavirus-covid-19-number-of-cases-in-scotland-$DATE.html data/daily/covid-19-cases-$DATE-scotland.csv
# Edit data/covid-19-totals-scotland.csv with output from running the following (double check numbers)
./tools/extract_totals.py data/raw/coronavirus-covid-19-number-of-cases-in-scotland-$DATE.html
```

Northern Ireland (2pm)

```bash
open https://www.publichealth.hscni.net/news/covid-19-coronavirus#situation-in-northern-ireland
# Edit data/covid-19-totals-northern-ireland.csv with output from running the following (double check numbers)
curl https://www.publichealth.hscni.net/news/covid-19-coronavirus -o ni-tmp.html
./tools/extract_totals.py ni-tmp.html
```

Consolidate and check

```bash
./tools/consolidate_daily_areas.py
./tools/check_totals.py
```
