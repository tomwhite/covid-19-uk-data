
Data sources for historical data (not just current day's data).

|                      | Tests            | Cases                | Deaths               |
|----------------------|------------------|----------------------|----------------------|
|UK total              | OWID<sup>1</sup> | PHE JSON<sup>2</sup> | PHE JSON<sup>3</sup> |
|England total         | -                | PHE JSON             | PHE JSON             |
|England UTLAs         | -                | PHE JSON             | -                    |
|Scotland total        | Trends XLSX      | Trends XLSX          | PHE JSON             |
|Scotland HBs          | -                | Boards XLSX          | -                    |
|Wales total           | PHW XLSX         | PHW XLSX             | PHE JSON             |
|Wales HBs<sup>4</sup> | -                | PHW XLSX             | -                    |
|NI total<sup>5</sup>  | -                | -                    | PHE JSON             |
|NI LGDs               | -                | -                    | -                    |

1. The PHE CSV/JSON download does not have historical data for UK tests, so we get it from Our World in Data. OWID gets the data from PHE.
2. UK total cases is only published for the current day (not historical).
3. The PHE JSON feed is used rather than the CSV files, since the CSVs files don't contain UK-level deaths.
4. Wales publishes at the local authority level, but this repo publishes at the health board (HB) level.
5. NI publishing is currently broken, and there is no machine-readable feed for test or case numbers.

URLs are subject to change and can be found in _crawl_all.py_.
