#!/usr/bin/env bash

if [[ "$#" -lt 1 ]]; then
    echo "Usage: ./tools/update_all.sh [<source>]"
    exit 1
fi

./tools/crawl_all.py "$@"
./tools/convert_sqlite_to_csvs.py
if git diff-index --quiet HEAD data/*.csv ; then
    git checkout data/covid-19-uk.db
else
    git diff
    printf "\a" # beep
fi