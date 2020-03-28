#!/usr/bin/env bash

if [[ "$#" -lt 1 ]]; then
    echo "Usage: ./tools/update.sh <Country> [<Date>]"
    exit 1
fi

COUNTRY=$1
DATE=${2:-$(date +'%Y-%m-%d')}
if ! ./tools/crawl.py $DATE $COUNTRY; then
    exit $?
fi
./tools/convert_sqlite_to_csvs.py
git diff
read -p "Commit changes? [y/n] " yn
case $yn in
    [Yy]* )
        git add data
        git commit -am "Update for $DATE for $COUNTRY"
        echo "Changes committed"
        ;;
    * )
        echo "Changes not committed"
        ;;
esac