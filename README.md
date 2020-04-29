# COVID-19 UK Historical Data

Data on numbers of tests, confirmed cases, and deaths for coronavirus (COVID-19) in the UK is published by the government, but it is fragmented and not always provided in consistent or machine-friendly formats. Also, in many cases only the latest numbers are available so it's not possible to look at changes over time.

This site collates the historical data and provides it in an easily consumable format (CSV), in both wide and [tidy data](https://en.wikipedia.org/wiki/Tidy_data) forms.

Ideally the data publishers will start doing this so this site becomes redundant.

## Data files

The following CSV files are available:

* [data/covid-19-cases-uk.csv](data/covid-19-cases-uk.csv): daily counts of confirmed cases for (upper tier) local authorities in England, health boards in Scotland and Wales, and local government district for Northern Ireland.
    * Note that prior to 18 March 2020 Wales data was broken down by local authority, not heath board, and prior to 27 March 2020 there were no breakdowns by area for Northern Ireland.
* [data/covid-19-totals-uk.csv](data/covid-19-totals-uk.csv): daily counts of tests, confirmed cases, deaths for the whole of the UK
* [data/covid-19-totals-england.csv](data/covid-19-totals-england.csv): daily counts of tests, confirmed cases, deaths for England
* [data/covid-19-totals-northern-ireland.csv](data/covid-19-totals-northern-ireland.csv): daily counts of tests, confirmed cases, deaths for Northern Ireland
* [data/covid-19-totals-scotland.csv](data/covid-19-totals-scotland.csv): daily counts of tests, confirmed cases, deaths for Scotland
* [data/covid-19-totals-wales.csv](data/covid-19-totals-wales.csv): daily counts of tests, confirmed cases, deaths for Wales
* [data/covid-19-indicators-uk.csv](data/covid-19-indicators-uk.csv): daily counts of tests, confirmed cases, deaths for the whole of the UK and individual countries in the UK (England, Scotland, Wales, Northern Ireland). This is a tidy-data version of _covid-19-totals-*.csv_ combined into one file.
* _data/daily/*.csv_: daily counts, with a separate file for each date and country.
    * No longer being published since 23 April 2020. Use [data/covid-19-cases-uk.csv](data/covid-19-cases-uk.csv)

Interpreting the numbers (more information on this [DHSC/PHE page](https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public#number-of-cases-and-deaths), and the [PHE dashboard about page](https://coronavirus.data.gov.uk/about))
* "Tests" are the number of people tested, not the number of samples tested.
* "Confirmed cases" are the number of people with a positive test.
* "Deaths" are hospital deaths, so they don't include deaths of people with COVID-19 who died at home for example.

You can use these files without reading the rest of this document.

There is an *experimental* [Datasette instance](https://covid-19-uk-datasette-65tzkjlxkq-ew.a.run.app/) hosting the data. This is useful for running simple SQL on the data, or exporting in JSON format.

## News

* 28 April 2020. The NI Department of Health is no longer reporting the number of people tested, just the number of tests.
* 21 April 2020. The PHA NI dashboard was [suspended](https://twitter.com/healthdpt/status/1252624119335706625) since it was reporting incorrect data. Test and total confirmed case numbers are being announced on Twitter by [@healthdpt](https://twitter.com/healthdpt). Area breakdowns are no longer being provided.
* 21 April 2020. The [PHW dashboard][PHW-dashboard] now has a link to download the data in XLSX format. The URL is dynamically generated however, so it's still not easy to automate the download.
* 20 April 2020. The [PHE dashboard][PHE-dashboard] now has stable URLs for its CSV downloads.
* 18 April 2020. PHA NI launched a [dashboard](http://www.pha.site/cvdashboard) to replace the daily surveillance reports. 
* 15 April 2020. A new [dashboard][PHE-dashboard] for UK and England was launched, replacing the ArcGIS one. As a part of this change the XLSX/CSV files for daily indicators, and case counts by region and UTLA (in England) are no longer being produced. They have been replaced by CSV files, or - for programmatic access - a JSON feed.
* 14 April 2020. No per-area case numbers produced for NI, even though it is a weekday (Tuesday). Yesterday was a bank holiday, and no case numbers were produced either.
* 9 April 2020. The reporting period for case numbers in Wales changed. "For operational reasons, we are moving the point at which we count new cases of Novel Coronavirus (Covid-19) back from 7pm to 1pm.  Case numbers on Thursday [9 April] will therefore be lower than usual, and will return to normal on Friday [10 April]."
* 8 April 2020. Scotland started publishing numbers for people in hospital and intensive care, by health board. They also started reporting numbers that were less 5 as "*".
* 6 April 2020. Wales published a new interactive [dashboard][PHW-dashboard], which gives data for confirmed cases, and testing episodes, broken down by local authority and health board. There is historical data too. Unfortunately there is currently no way of exporting the raw data from the dashboard.
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

* _Public Health England:_ Add testing numbers (including historical) to the [dashboard][PHE-dashboard] and CSV downloads.

* _Public Health Wales:_ Provide the data download for the [dashboard][PHW-dashboard] at a stable URL.

* _Public Health Scotland_: Add numbers of deaths to the [Trends in daily COVID-19 data][Scotland-trends] file.

* _Public Health Agency, Northern Ireland:_ Provide a machine readable version of the historical data in the [surveillance bulletins][NI-surveillance-bulletins].

## Data sources and the collation process

A lot of the collation process is manual, however there are a few command line tools to help process the data into its final form. The data sources are changing from day to day, which means the process is constantly changing.

Raw data (including HTML pages, PDFs, CSV and XLSX files), is archived under _data/raw_, it should never be edited.

### UK

* Number of **tests, confirmed cases and deaths** are published at [https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public#number-of-cases](https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public#number-of-cases) at 2pm in HTML format
* Number of historical **confirmed cases and deaths** are published on the [PHE dashboard][PHE-dashboard] in the afternoon in CSV format (powered by a backend JSON feed)
* Twitter updates: [@DHSCgovuk](https://twitter.com/DHSCgovuk)

### England

* Number of **tests** are not published
* Number of **confirmed cases and deaths** are published on the [PHE dashboard][PHE-dashboard] in the afternoon in CSV format
* Number of **confirmed cases by local authority** are published on the [PHE dashboard][PHE-dashboard] in the afternoon in CSV format
* Twitter updates: [@PHE_uk](https://twitter.com/PHE_uk)

### Scotland

* Number of **tests, confirmed cases and deaths**, and **confirmed cases by local authority**, are published at [https://www.gov.scot/publications/trends-in-number-of-people-in-hospital-with-confirmed-or-suspected-covid-19/](https://www.gov.scot/publications/trends-in-number-of-people-in-hospital-with-confirmed-or-suspected-covid-19/) at 2pm in XLSX format
* Twitter updates: [@scotgov](https://twitter.com/scotgov)

### Wales

* Number of **tests, confirmed cases and deaths**, and **confirmed cases by local authority and health board**, are published on the [PHW dashboard][PHW-dashboard] at 2pm, with an accompanying XLSX download.
* Twitter updates: [@PublicHealthW](https://twitter.com/publichealthw)

### Northern Ireland

* ~~Number of **tests, confirmed cases and deaths**, and **confirmed cases by local authority** are published in the [surveillance bulletin][NI-surveillance-bulletins] at 2pm in PDF format (old bulletins are archived)~~ Not currently being updated.
* Twitter updates: [@healthdpt](https://twitter.com/healthdpt)

### Local Authority and Health Board metadata

* English and Welsh local authorities: [Lower Tier Local Authority to Upper Tier Local Authority (April 2019) Lookup in England and Wales](http://geoportal1-ons.opendata.arcgis.com/datasets/lower-tier-local-authority-to-upper-tier-local-authority-april-2019-lookup-in-england-and-wales/data)
* Scottish Health Boards: [Health Board 2014](https://www.opendata.nhs.scot/dataset/geography-codes-and-labels/resource/652ff726-e676-4a20-abda-435b98dd7bdc)
* Welsh Health Boards: [Local Health Boards (April 2019) Names and Codes in Wales](https://geoportal.statistics.gov.uk/datasets/local-health-boards-april-2019-names-and-codes-in-wales)
* Northern Irish Local Government Districts: [Local Government Districts (December 2016) Names and Codes in Northern Ireland](https://data.gov.uk/dataset/923eca81-ca9c-44a9-921e-031d28fafd1e/local-government-districts-december-2016-names-and-codes-in-northern-ireland)

## Related projects/datasets

* NHS England [daily deaths by trust and region](https://www.england.nhs.uk/statistics/statistical-work-areas/covid-19-daily-deaths/)
* National Records of Scotland: [Deaths involving coronavirus (COVID-19) in Scotland](https://www.nrscotland.gov.uk/covid19stats)
* ONS: [Deaths registered weekly in England and Wales, provisional](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/datasets/weeklyprovisionalfiguresondeathsregisteredinenglandandwales)
* NISRA: [Weekly Deaths](https://www.nisra.gov.uk/publications/weekly-deaths)
* The [PHE dashboard][PHW-dashboard] is [open source](https://github.com/PublicHealthEngland/coronavirus-dashboard).
* Ian Watt's [COVID-19 Scotland dataset](https://github.com/watty62/Scot_covid19)
* Emma Doughty's [UK COVID-19 data](https://github.com/emmadoughty/Daily_COVID-19)
* ODI Leeds mirror of PHE dashboard data: https://github.com/odileeds/coronavirus-data

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
./tools/update.sh UK-cases-and-deaths
```

The equivalent done manually (just for Wales):
```bash
DATE=$(date +'%Y-%m-%d')
./tools/crawl.py $DATE Wales
./tools/convert_sqlite_to_csvs.py
git add data/; git commit -am "Update for $DATE for Wales"
```

NI updates are being done manually since there are currently no machine-readable sources.
```bash
# edit covid-19-totals-northern-ireland.csv and add tests/cases/deaths
./tools/convert_totals_to_indicators.py
csvs-to-sqlite --replace-tables -t indicators -pk Date -pk Country -pk Indicator data/covid-19-indicators-uk.csv data/covid-19-uk.db
./tools/convert_sqlite_to_csvs.py
git commit -a # "Update for xxx for NI from https://twitter.com/healthdpt"
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

Compare with historical PHE data
```bash
./tools/compare_phe_historical_json.py
```

Compare with historical PHS data
```bash
curl -L https://www.gov.scot/binaries/content/documents/govscot/publications/statistics/2020/04/trends-in-number-of-people-in-hospital-with-confirmed-or-suspected-covid-19/documents/trends-in-number-of-people-in-hospital-with-confirmed-or-suspected-covid-19/trends-in-number-of-people-in-hospital-with-confirmed-or-suspected-covid-19/govscot%3Adocument/HSCA%2B-%2BSG%2BWebsite%2B-%2BIndicator%2BTrends%2Bfor%2Bdaily%2Bdata%2Bpublication.xlsx -o "data/raw/phs/HSCA+-+SG+Website+-+Indicator+Trends+for+daily+data+publication.xlsx"
./tools/compare_phs_historical.py
```

### Manual overrides

Sometimes it's necessary to fix data by hand. In this case the following tools are useful:

Repopulate the sqlite database from the CSV files:
```bash
rm data/covid-19-uk.db
csvs-to-sqlite --replace-tables -t indicators -pk Date -pk Country -pk Indicator data/covid-19-indicators-uk.csv data/covid-19-uk.db
csvs-to-sqlite --replace-tables -t cases -pk Date -pk Country -pk AreaCode -pk Area data/covid-19-cases-uk.csv data/covid-19-uk.db
```

[NI-surveillance-bulletins]: https://www.publichealth.hscni.net/publications/covid-19-surveillance-reports
[PHE-dashboard]: https://coronavirus.data.gov.uk/
[PHW-dashboard]: https://public.tableau.com/profile/public.health.wales.health.protection#!/vizhome/RapidCOVID-19virology-Public/Headlinesummary
[Scotland-trends]: https://www.gov.scot/publications/trends-in-number-of-people-in-hospital-with-confirmed-or-suspected-covid-19/