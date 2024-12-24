drop view if exists Change;

create view Change(
  store
, code
, name
, changes
, prices
, min_price
, max_price
, "%change"
) as
with MinMax as (
  select
    store
  , code
  , name
  , count(*) as changes
  , group_concat(trim(price, ' each per pound lb'), ' ') as prices
  , min(cast(trim(price, '$ each per pound lb') as real)) as min_price
  , max(cast(trim(price, '$ each per pound lb') as real)) as max_price
  from (
    select
      store
    , date(previous_when) as "before"
    , date(when_begin_iso) as "after"
    , code
    , name
    , size
    , price
    , previous_size
    , previous_price
    from (
      select
        store.id as store
      , sesh.when_begin_iso
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
        inner join ScrapedStore store on sesh.store = store.id) Staggered
    where price != previous_price or size != previous_size
    order by store, code desc, when_begin_iso
  ) Changes
  group by store, code, name
  order by changes desc
)
select
  *
, round((max_price - min_price) / min_price * 100, 1) as "%change"
from MinMax
order by "%change" desc;

