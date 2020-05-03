#!/usr/bin/env bash

if [[ "$#" -lt 1 ]]; then
    echo "Usage: ./tools/update_all.sh [<source>]"
    exit 1
fi

SOURCE=$1
DATE=$(date +'%Y-%m-%d')

./tools/crawl_all.py "$@"
./tools/convert_sqlite_to_csvs.py
if git diff --quiet HEAD data/*.csv; then
    git checkout data/covid-19-uk.db
else
    printf "\a" # beep
    git diff
    read -p "Commit changes? [y/n] " yn
    case $yn in
        [Yy]* )
            git add data
            git commit -am "Update for $DATE for $SOURCE"
            echo "Changes committed"
            ;;
        * )
            echo "Changes not committed"
            ;;
    esac
fi
