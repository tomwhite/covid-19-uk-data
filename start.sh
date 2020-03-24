datasette serve data/covid-19-uk.db \
  -p 3000 \
  --cors \
  --config default_cache_ttl:0
