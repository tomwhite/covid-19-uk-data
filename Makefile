.PHONY: dev-setup \
england-ua-dailies-download \
england-ua-dailies-generate \
england-ua-dailies \
england-totals-download \
england-totals-generate \
england-totals-cleanup \
england-totals \
england-all

DATE=$(shell date +'%Y-%m-%d')
ENGLAND_UA_URL=https://www.arcgis.com/sharing/rest/content/items/b684319181f94875a6879bbc833ca3a6/data
ENGLAND_UA_RAW_CSV=./data/raw/CountyUAs_cases_table-$(DATE).csv
ENGLAND_UA_CSV=./data/daily/covid-19-cases-$(DATE)-england.csv
ENGLAND_TOTALS_URL=https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public
ENGLAND_TOTALS_TEMP_HTML=./data/raw/uk-totals-temp-$(DATE).html

england-ua-dailies-download:
	@echo ">>> Downloading England UA Dailies\n"
	@curl $(ENGLAND_UA_URL) -o ./data/raw/CountyUAs_cases_table-$(DATE).csv

england-ua-dailies-generate:
	@echo ">>> Generating England UA Dailies\n"
	@make dev-setup
	@. venv/bin/activate && \
		python ./tools/gen_daily_areas_england.py $(ENGLAND_UA_RAW_CSV) $(ENGLAND_UA_CSV)

england-ua-dailies:
	@make england-ua-dailies-download
	@make england-ua-dailies-generate

england-totals-download:
	@echo ">>> Downloading England Totals\n"
	@curl $(ENGLAND_TOTALS_URL) -o $(ENGLAND_TOTALS_TEMP_HTML)

england-totals-generate:
	@make dev-setup
	@. venv/bin/activate && \
	python ./tools/extract_totals.py $(ENGLAND_TOTALS_TEMP_HTML)

england-totals-cleanup:
	@echo ">>> Removing temp England totals HTML\n"
	@rm -f $(ENGLAND_TOTALS_TEMP_HTML)

england-totals:
	@make england-totals-download
	@make england-totals-generate
	@make england-totals-cleanup

england-all:
	@make england-ua-dailies
	@make england-totals

dev-setup:
	@python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
