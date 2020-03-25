datasette serve data/covid-19-uk.db \
  -m metadata.json \
  -p 3000 \
  --cors \
  --config default_cache_ttl:0
