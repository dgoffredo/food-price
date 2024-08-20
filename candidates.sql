-- This query returns stores in the order of "most need scraping" first.
-- If a store has never had its catalog scraped, then it appears first.
-- Lower store codes take priority.
-- If a store has had its catalog scraped before, then the stores for which
-- it's been the longest take priority.
-- The query returns all columns for the most recent ScrapedStore having the
-- corresponding store code.
with CandidateStore as (
  select store2.code, store2.id, max(session.when_begin_iso) as last_scraped
  from ScrapedStore store left join ScrapeSession session
    on store.id = session.store
  inner join ScrapedStore store2 on store2.code  = store.code
  group by store.code, store.when_iso
  having store2.when_iso = max(store.when_iso))
select store.id, store.code, url.domain, url.slug
from ScrapedStore store inner join CandidateStore candidate
  on store.id = candidate.id
inner join StoreURL url
  on url.id = store.url
order by candidate.last_scraped, candidate.code;
