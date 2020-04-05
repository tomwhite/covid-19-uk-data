# COVID-19 UK Historical Data

Data on testing and case numbers for coronavirus (COVID-19) in the UK is published by the government, but it is fragmented and not always provided in consistent or machine-friendly formats. Also, in many cases only the latest numbers are available so it's not possible to look at changes over time.

This site collates the historical data and provides it in an easily consumable format (CSV), in both wide and [tidy data](https://en.wikipedia.org/wiki/Tidy_data) forms.

Ideally the data publishers will start doing this so this site becomes redundant.

## Data files

The following CSV files are available:

* [data/covid-19-cases-uk.csv](data/covid-19-cases-uk.csv): daily counts of confirmed cases for (upper tier) local authorities in England, health boards in Scotland and Wales, and local government district for Northern Ireland.
    * Note that prior to 18 March 2020 Wales data was broken down by local authority, not heath board, and prior to 27 March 2020 there were breakdowns by area for Northern Ireland.
* [data/covid-19-totals-uk.csv](data/covid-19-totals-uk.csv): daily counts of tests, confirmed cases, deaths for the whole of the UK
* [data/covid-19-totals-england.csv](data/covid-19-totals-england.csv): daily counts of tests, confirmed cases, deaths for England
* [data/covid-19-totals-northern-ireland.csv](data/covid-19-totals-northern-ireland.csv): daily counts of tests, confirmed cases, deaths for Northern Ireland
* [data/covid-19-totals-scotland.csv](data/covid-19-totals-scotland.csv): daily counts of tests, confirmed cases, deaths for Scotland
* [data/covid-19-totals-wales.csv](data/covid-19-totals-wales.csv): daily counts of tests, confirmed cases, deaths for Wales
* [data/covid-19-indicators-uk.csv](data/covid-19-indicators-uk.csv): daily counts of tests, confirmed cases, deaths for the whole of the UK and individual countries in the UK (England, Scotland, Wales, Northern Ireland). This is a tidy-data version of _covid-19-totals-*.csv_ combined into one file.
* _data/daily/*.csv_: daily counts, with a separate file for each date and country.

You can use these files without reading the rest of this document.

There is an *experimental* [Datasette instance](https://covid-19-uk-data.glitch.me/) hosting the data. This is useful for running simple SQL on the data, or exporting in JSON format. Note that there may be a lag in publishing the data to Datasette.

## News

* 2 April 2020. Scotland [reported a more timely process for counting deaths](https://www.gov.scot/news/new-process-for-reporting-covid-19-deaths/).
* 29 March 2020. There's a [new spreadsheet](https://fingertips.phe.org.uk/documents/Historic%20COVID-19%20Dashboard%20Data.xlsx) that includes historical data for the dashboard. This includes cases (by country, English UTLA, English NHS region), deaths (by country), and recovered patients (although this isn't being updated at the time of writing).
* 27 March 2020. UK daily indicators now include number of deaths for UK, England, Scotland, Wales, and Northern Ireland.
* 26 March 2020. Northern Ireland's Public Health Agency (PHA) started publishing confirmed cases by Local Government District (LGD) on weekdays.
* 25 March 2020. The reporting period for number of deaths changed. Previously it was for the 24 hour period starting and ending at 9am. The new period starts and ends at 5pm, and is reported the following afternoon at 2pm. (So the number of deaths reported on 25 March (cumulative total 463) represents the period 9am to 5pm on 24 March.) The testing and case numbers continue to be the 9am period.
* 24 March 2020. Northern Ireland's Public Health Agency (PHA) started producing a Daily COVID-19 Surveillance Bulletin in PDF form. It contains test numbers (also broken down by Health and Social Care Trust), and case numbers *but only on a choropleth map* (and broken down by age and gender).
* 21 March 2020. PHW is back to health board (not LA) breakdowns again, this time it looks permanent.
* 20 March 2020. PHW is providing LA area breakdowns again, after not doing so for two days.
* 18 March 2020. PHW is no longer providing LA area breakdowns. "Novel Coronavirus (COVID-19) is now circulating in every part of Wales. For this reason, we will not be reporting cases by local authority area from today. From tomorrow, we will update daily at 12 noon the case numbers by health board of residence."

## Wishlist

Here are my suggestions for how to improve the data being published by public bodies.

The short version: **publish everything in CSV format, and include historical data!**

Department of Health and Social Care, and Public Health England
1. ~~Publish historical data, not just the current day's data.~~ _New spreadsheet of historical data since 29 March 2020._
2. ~~Add a column for number of recovered patients to the [daily indicators](https://www.arcgis.com/home/item.html?id=bc8ee90225644ef7a6f4dd1b13ea1d67). (It is published on the dashboard, but nowhere else.)~~ _Provided in the new spreadsheet of historical data since 29 March 2020 - but not being updated at the time of writing._
3. Publish deaths by hospital every day.

Public Health Wales
1. Publish the number of tests being performed every day.
2. Publish daily totals (tests, confirmed cases, deaths) in machine readable form (CSV).
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
2. Publish confirmed cases by local authority/health board in machine readable form (CSV). ~~These are not currently being published, so it would be good to be able to get these figures, even if just on a web page.~~ _Published by LGD on weekdays since 26 March 2020._
3. ~~Publish historical data, not just the current day's data.~~ _An archive of surveillance bulletins is being published since 24 March 2020._
4. Publish deaths by hospital every day.

## Data sources and the collation process

A lot of the collation process is manual, however there are a few command line tools to help process the data into its final form. The data sources are changing from day to day, which means the process is constantly changing.

Raw data (including HTML pages, PDFs, CSV and XLSX files), is archived under _data/raw_, it should never be edited.

### UK

* Number of **tests, confirmed cases and deaths** are published at [https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public#number-of-cases](https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public#number-of-cases) at 2pm in HTML format
* Number of historical **confirmed cases and deaths** are published in the [historical dashboard data](https://fingertips.phe.org.uk/documents/Historic%20COVID-19%20Dashboard%20Data.xlsx) at 6pm in XLSX format
* Twitter updates: [@DHSCgovuk](https://twitter.com/DHSCgovuk)

### England

* Number of **tests** are not published
* Number of **confirmed cases and deaths** are published in the [daily indicators](https://www.arcgis.com/home/item.html?id=bc8ee90225644ef7a6f4dd1b13ea1d67) at 6pm in XLSX format
* Number of **confirmed cases by local authority** are published in the [UTLA cases table](https://www.arcgis.com/home/item.html?id=b684319181f94875a6879bbc833ca3a6) at 6pm in CSV format
    * Note that prior to 11 March 2020 case numbers were published in HTML format.
* Twitter updates: [@PHE_uk](https://twitter.com/PHE_uk)

### Scotland

* Number of **tests, confirmed cases and deaths**, and **confirmed cases by local authority**, are published at [www.gov.scot/coronavirus-covid-19](https://www.gov.scot/coronavirus-covid-19/) at 2pm in HTML format
* Twitter updates: [@scotgov](https://twitter.com/scotgov)

### Wales

* Number of **tests** are not published
* Number of **confirmed cases and deaths**, and **confirmed cases by local authority**, are published at [https://covid19-phwstatement.nhs.wales/](https://covid19-phwstatement.nhs.wales/) at 2pm in HTML format
* Twitter updates: [@PublicHealthW](https://twitter.com/publichealthw)

### Northern Ireland

* Number of **tests, confirmed cases and deaths**, and **confirmed cases by local authority** are published in the daily surveillance bulletin at [https://www.publichealth.hscni.net/publications/covid-19-surveillance-reports](https://www.publichealth.hscni.net/publications/covid-19-surveillance-reports) at 2pm in PDF format (old bulletins are archived)
* Twitter updates: [@publichealthni](https://twitter.com/publichealthni)

Note that [daily indicators](https://www.arcgis.com/home/item.html?id=bc8ee90225644ef7a6f4dd1b13ea1d67) includes **confirmed cases and deaths** for UK, and England, Scotland, Wales, and Northern Ireland.

### By URL

|URL|What|When|Format|Archived?|
|---|----|----|------|---------|
|https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public|UK tests, confirmed cases, deaths|2pm|HTML|Yes|
|https://fingertips.phe.org.uk/documents/Historic%20COVID-19%20Dashboard%20Data.xlsx|cases (by country, English UTLA, English NHS region), deaths (by country) ("historical dashboard data")|6pm|XLSX|No|
|https://www.arcgis.com/sharing/rest/content/items/bc8ee90225644ef7a6f4dd1b13ea1d67/data|UK tests, UK/England/Scotland/Wales/NI confirmed cases, UK/England/Scotland/Wales/NI deaths ("daily indicators")|6pm|XLSX|No|
|https://www.arcgis.com/sharing/rest/content/items/b684319181f94875a6879bbc833ca3a6/data|England confirmed cases by local authority ("UTLA cases table")|6pm|CSV|No|
|https://www.arcgis.com/sharing/rest/content/items/ca796627a2294c51926865748c4a56e8/data|England confirmed cases by NHS region ("NHA regional cases table")|6pm|CSV|No|
|https://www.gov.scot/coronavirus-covid-19/|Scotland tests, confirmed cases, deaths, confirmed cases by local authority|2pm|HTML|Yes|
|https://covid19-phwstatement.nhs.wales/|Wales confirmed cases, deaths, confirmed cases by local authority|2pm|HTML|Yes|
|https://www.publichealth.hscni.net/publications/covid-19-surveillance-reports|Northern Ireland tests, confirmed cases, deaths, confirmed cases by local authority|2pm|PDF|Yes|

Note that the arcgis.com links are direct links to the data.

### Local Authority and Health Board metadata

* English and Welsh local authorities: [Lower Tier Local Authority to Upper Tier Local Authority (April 2019) Lookup in England and Wales](http://geoportal1-ons.opendata.arcgis.com/datasets/lower-tier-local-authority-to-upper-tier-local-authority-april-2019-lookup-in-england-and-wales/data)
* Scottish Health Boards: [Health Board 2014](https://www.opendata.nhs.scot/dataset/geography-codes-and-labels/resource/652ff726-e676-4a20-abda-435b98dd7bdc)
* Welsh Health Boards: [Local Health Boards (April 2019) Names and Codes in Wales](https://geoportal.statistics.gov.uk/datasets/local-health-boards-april-2019-names-and-codes-in-wales)
* Northern Irish Local Government Districts: [Local Government Districts (December 2016) Names and Codes in Northern Ireland](https://data.gov.uk/dataset/923eca81-ca9c-44a9-921e-031d28fafd1e/local-government-districts-december-2016-names-and-codes-in-northern-ireland)

## Related projects

* Ian Watt's [COVID-19 Scotland dataset](https://github.com/watty62/Scot_covid19)
* Emma Doughty's [UK COVID-19 data](https://github.com/emmadoughty/Daily_COVID-19)

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

The **updates** tool runs **crawl** then **convert_sqlite_to_csvs**, and issues interactive prompts for if you want to commit the changes to git.

```bash
./tools/update.sh Wales
./tools/update.sh Scotland
./tools/update.sh NI
./tools/update.sh UK
./tools/update.sh UK-daily-indicators
./tools/update.sh England
DATE=$(date +'%Y-%m-%d')
curl -L https://www.arcgis.com/sharing/rest/content/items/ca796627a2294c51926865748c4a56e8/data -o data/raw/NHSR_Cases_table-$DATE.csv
```

The equivalent done manually (just for Wales):
```bash
DATE=$(date +'%Y-%m-%d')
./tools/crawl.py $DATE Wales
./tools/convert_sqlite_to_csvs.py
git add data/; git commit -am "Update for $DATE for Wales"
```

Updates are not always made at a consistent time of day, so the following command can be run continuously in a terminal to check for updates every 10 minutes. The `-b` option makes it beep if there is a new update.
```bash
watch -n 600 -b ./tools/crawl.py
```

Check data consistency
```bash
./tools/check_indicators.py
./tools/check_totals.py
```

Update Dataset instance: https://glitch.com/edit/#!/covid-19-uk-data, then click on Tools > Terminal
```bash
curl https://raw.githubusercontent.com/tomwhite/covid-19-uk-data/master/data/covid-19-uk.db -o data/covid-19-uk.db
```
Check: https://covid-19-uk-data.glitch.me/

### Manual overrides

Sometimes it's necessary to fix data by hand. In this case the following tools are useful:

Repopulate the sqlite database from the CSV files:
```bash
rm data/covid-19-uk.db
csvs-to-sqlite --replace-tables -t indicators -pk Date -pk Country -pk Indicator data/covid-19-indicators-uk.csv data/covid-19-uk.db
csvs-to-sqlite --replace-tables -t cases -pk Date -pk Country -pk AreaCode -pk Area data/covid-19-cases-uk.csv data/covid-19-uk.db
```
