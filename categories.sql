with EntryCategorized as (
select *,
  coalesce(
  re_matchi('Price not available', price, 'NO_PRICE'),
  re_matchi('\$[.0-9]+\s+per\s+lb', price, 'PER_POUND'),
  re_matchi('\$[.0-9]+\s+each', price, 'EACH'),
  'OTHER') as price_category,
  coalesce(
  re_matchi('LB', size, 'MASS_POUNDS'),
  re_matchi('[.0-9]+\s+LBS?', size, 'MASS_POUNDS'),
  re_matchi('[.0-9]+\s+(OZ|M)', size, 'MASS_OUNCES'),
  re_matchi('([0-9]+\s+X\s+)[.0-9]+\s+OZ', size, 'MASS_OUNCES_TIMES_N'),
  re_matchi('[.0-9]+\s+G', size, 'MASS_GRAMS'),
  re_matchi('[.0-9]+\s+KG', size, 'MASS_KILOGRAMS'),
  re_matchi('[.0-9]+\s+(FL( OZ)?|OZA)', size, 'VOLUME_OUNCES'),
  re_matchi('([0-9]+\s+X\s+)[.0-9]+\s+FL\s+O\s*Z', size, 'VOLUME_OUNCES_TIMES_N'),
  re_matchi('[.0-9]+\s+ML', size, 'VOLUME_MILLILITERS'),
  re_matchi('[.0-9]+\s+L', size, 'VOLUME_LITERS'),
  re_matchi('[.0-9]+\s+PT', size, 'VOLUME_PINTS'),
  re_matchi('[.0-9]+\s+QT', size, 'VOLUME_QUARTS'),
  re_matchi('[.0-9]+\s+GLL', size, 'VOLUME_GALLONS'),
  re_matchi('[.0-9]+\s+G/L', size, 'VOLUME_GALLONS'),
  re_matchi('[.0-9]+\s+SF', size, 'AREA_SQUARE_FEET'),
  re_matchi('[.0-9]+\s+FT', size, 'LENGTH_FEET'),
  re_matchi('[.0-9]+\s+YD', size, 'LENGTH_YARDS'),
  re_matchi('[.0-9]+\s+(CT|EA)', size, 'QUANTITY'),
  re_matchi('[.0-9]+\s+DZ', size, 'QUANTITY_TIMES_TWELVE'),
  re_match('', size, 'NO_SIZE'),
  'OTHER') as size_category
from ScrapedCatalogEntry)

select size_category, price_category, count(*) as freq
from EntryCategorized
group by size_category, price_category
order by freq;

