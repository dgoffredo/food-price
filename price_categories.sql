select coalesce(
  re_matchi('Price not available', price, 'NO_PRICE'),
  re_matchi('\$[.0-9]+\s+per\s+lb', price, 'PER_POUND'),
  re_matchi('\$[.0-9]+\s+each', price, 'EACH'),
  'OTHER: ' || price) as category
from ScrapedCatalogEntry
where category like 'OTHER: %';
