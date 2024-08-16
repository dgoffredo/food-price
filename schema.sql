create table if not exists ScrapeSessionLog(
  id integer primary key not null,
  -- the exit status and stderr of the Puppeteer NodeJS script scrape.mjs
  scrape_status int,
  scrape_stderr text,
  -- the exit status and stderr of the BeautifulSoup Python script parse.py
  parse_status int,
  parse_stderr text,
  -- the exit status and stderr of the SQLite Python script persist.py
  persist_status int,
  persist_stderr text);

create table if not exists ScrapeSession(
  id integer primary key not null,
  log integer,
  when_begin_iso text not null,
  when_end_iso text,

  foreign key (log) references ScrapeSessionLog(id));

create table if not exists ScrapedCatalogEntry(
  scrape_session int not null,
  name text,
  size text,
  price text,
  cart_code text,
  product_page_path text,
  -- If product_page_path is '/foo/bar/baz', then code is 'baz'.
  -- Without pattern extraction, the following is the only way to do this.
  code text as (replace(product_page_path, rtrim(product_page_path, replace(product_page_path, '/', '')), '')),

  foreign key (scrape_session) references ScrapeSession(id),
  -- Rows are unique.
  unique (scrape_session, name, size, price, cart_code, product_page_path));
