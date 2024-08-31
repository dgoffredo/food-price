with MinMax as (
  select
    code
  , name
  , count(*) as changes
  , group_concat(trim(price, ' each per pound lb'), ' ') as prices
  , min(cast(trim(price, '$ each per pound lb') as real)) as min_price
  , max(cast(trim(price, '$ each per pound lb') as real)) as max_price
  from (
    select
      date(previous_when) as "before"
    , date(when_begin_iso) as "after"
    , code
    , name
    , size
    , price
    , previous_size
    , previous_price
    from (
      select
        sesh.when_begin_iso
      , lag(sesh.when_begin_iso) over (partition by store.code, entry.code order by sesh.when_begin_iso) as previous_when
      , entry.code
      , name.name
      , lag(entry.size) over (partition by store.code, entry.code order by sesh.when_begin_iso) as previous_size
      , entry.size
      , lag(entry.price) over (partition by store.code, entry.code order by sesh.when_begin_iso) as previous_price
      , entry.price
      from ScrapedCatalogEntry entry
        inner join ScrapeSession sesh on entry.scrape_session = sesh.id
        inner join ScrapedCatalogEntryName name on entry.name = name.id
        inner join ScrapedStore store on sesh.store = store.id where store.code = 566) Staggered
    where price != previous_price or size != previous_size
    order by code desc, when_begin_iso
  ) Changes
  group by code, name
  order by changes desc
)
select
  *
, round((max_price - min_price) / min_price * 100, 1) as "%change"
from MinMax
order by "%change" desc
limit 38;

