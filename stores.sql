create table if not exists StoreURL(
  id integer primary key not null,
  -- url is the full URL scraped from the list of stores.
  -- It will be of the form https://foo.keyfood.com/store, but this table does
  -- not assume that form.
  url text not null,
  -- If url is 'https://foo.bar.baz:443/store', then domain is 'foo.bar.baz'.
  domain text not null,
  -- If domain is foo.bar.baz, then slug is foo unless foo is 'www'.
  -- If foo is 'www' then slug is bar.
  -- slug is used as part of the store _catalog_ URL (as opposed to the store
  -- URL). I observed that bar is always 'keyfood'. If foo is 'www', then
  -- the store catalog URL contains 'keyfood' in the path, whereas is foo
  -- is something else then that value is used instead.
  -- Another way of saying this is that the domain pattern is
  -- <store>.keyfood.com, except when <store> is 'keyfood' the subdomain
  -- is 'www'. slug undoes that so that you can just use slug in the store
  -- catalog URL. There is no 'www' store.
  slug text not null,

  -- url could be the primary key, since domain and slug are functions of it.
  -- However, it's simpler to do the derivation outside of the database.
  unique (url)
);

create table if not exists StoreHours(
  id integer primary key not null,
  -- Opening and closing types are of the form hh:mm or null. There are three
  -- special cases to consider:
  --
  -- 1. If foo_open is null, then so is foo_close. It means that there was no
  --    information for that day in the scraped store hours. This will probably
  --    not happen.
  -- 2. foo_close might be greater than 23:59. This indicates that the store
  --    closes the following day. For example, if the store opens at 5:00 AM
  --    Monday and closes at 1:00 AM Tuesday, then monday_open will be '05:00'
  --    and monday_close will be '25:00'.
  -- 3. The store might be open for 24 hours on a day. Usually this means that
  --    the store is open 24 hours every day. If a store is open for 24 hours,
  --    then the opening time will be '00:00' and the closing time will be
  --    '24:00'.
  sunday_open text check (sunday_open is null or length(sunday_open) = 5),
  sunday_close text check (sunday_close is null or length(sunday_close) = 5),
  monday_open text check (monday_open is null or length(monday_open) = 5),
  monday_close text check (monday_close is null or length(monday_close) = 5),
  tuesday_open text check (tuesday_open is null or length(tuesday_open) = 5),
  tuesday_close text check (tuesday_close is null or length(tuesday_close) = 5),
  wednesday_open text check (wednesday_open is null or length(wednesday_open) = 5),
  wednesday_close text check (wednesday_close is null or length(wednesday_close) = 5),
  thursday_open text check (thursday_open is null or length(thursday_open) = 5),
  thursday_close text check (thursday_close is null or length(thursday_close) = 5),
  friday_open text check (friday_open is null or length(friday_open) = 5),
  friday_close text check (friday_close is null or length(friday_close) = 5),
  saturday_open text check (saturday_open is null or length(saturday_open) = 5),
  saturday_close text check (saturday_close is null or length(saturday_close) = 5),

  check ((sunday_open is null) = (sunday_close is null)),
  check ((monday_open is null) = (monday_close is null)),
  check ((tuesday_open is null) = (tuesday_close is null)),
  check ((wednesday_open is null) = (wednesday_close is null)),
  check ((thursday_open is null) = (thursday_close is null)),
  check ((friday_open is null) = (friday_close is null)),
  check ((saturday_open is null) = (saturday_close is null)),

  -- If two rows have the same hours, then they are the same.
  unique (sunday_open, sunday_close,
    monday_open, monday_close,
    tuesday_open, tuesday_close,
    wednesday_open, wednesday_close,
    thursday_open, thursday_close,
    friday_open, friday_close,
    saturday_open, saturday_close)
);

create table if not exists StoreAddress(
  id integer primary key not null,
  -- street_address is, e.g., '1234 Grocery Avenue'.
  street_address text,
  -- town (called "town" in the scraped data) is the name of the city or
  -- neighborhood, e.g. 'New York', 'Queens', or 'Ozone Park'.
  town text,
  -- state (called "region" in the scraped data) is the two character
  -- abbreviation of the US state, e.g. 'NY' or 'NJ'.
  state text,
  -- zip (called "postal" in the scraped data) is the ZIP postal code. It is
  -- either the 5-digit code or the extended 5+4 digit code with a separating
  -- hyphen.
  zip text,

  check (state is null or length(state) = 2),
  check (zip is null or length(zip) = 5 or length(zip) = 10),

  -- If two rows have the same non-id values, then they are the same.
  unique (street_address, town, state, zip));

create table if not exists ScrapedStore(
  -- Each store has a unique code, but since information about a store might
  -- change, the primary key of this table is separate.
  id integer primary key not null,
  when_iso text not null,
  code integer not null,
  name text,
  -- phone is the 10-digit hyphen-separated US phone number,
  -- e.g. '212-555-5555', or null if absent from the scraped data.
  phone text check (phone is null or length(phone) = 12),
  address integer, -- references StoreAddress(id)
  hours integer, -- references StoreHours(id)
  url integer, -- references StoreURL(id)

  foreign key (address) references StoreAddress(id),
  foreign key (hours) references StoreHours(id),
  foreign key (url) references StoreURL(id),

  -- If two rows have the same non-id values, then they are the same.
  unique (code, name, phone, address, hours, url)
);
