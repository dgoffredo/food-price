from bs4 import BeautifulSoup
import datetime
import json
import sqlite3
import string
import sys
import urllib.parse


def execute(db, query, params):
  print(query, file=sys.stderr)
  print(params, file=sys.stderr)
  print('-------', file=sys.stderr)
  return db.execute(query, params)


def make_address_id(db, street_address, town, state, zip):
  cursor = execute(db, """select id from StoreAddress where
  street_address is ? and
  town is ? and
  state is ? and
  zip is ?;
  """, (street_address, town, state, zip))
  rows = list(cursor)
  if len(rows) > 0:
    (id,), = rows
    return id
  # We have to insert a row.
  cursor = execute(db, """insert into StoreAddress(
  street_address,
  town,
  state,
  zip)
  values (?, ?, ?, ?);
  """, (street_address, town, state, zip))
  rowid = cursor.lastrowid
  (id,), = execute(db, "select id from StoreAddress where rowid = ?;", (rowid,))
  return id


def make_url_id(db, url):
  if url is None:
    return None
  cursor = execute(db, "select id from StoreURL where url = ?;", (url,))
  rows = list(cursor)
  if len(rows) > 0:
    (url_id,), = rows
    return url_id
  # We have to insert a value (url, domain, slug)
  parts = urllib.parse.urlparse(url)
  netloc = parts.netloc
  domain = netloc.split(':')[0]
  subdomains = domain.split('.')
  # TODO: Do we want to assume the number of subdomains?
  subdomain, _, _ = subdomains
  slug = 'keyfood' if subdomain == 'www' else subdomain
  cursor = execute(db, "insert into StoreURL(url, domain, slug) values(?, ?, ?);", (url, domain, slug))
  rowid = cursor.lastrowid
  (url_id,), = execute(db, "select id from StoreURL where rowid = ?;", (rowid,))
  return url_id


def format_time(hour, minute):
  return f'{hour:02}:{minute:02}'


def parse_day_hours(hours):
  if hours is None:
    return None, None
  if hours.lower() == 'open 24 hours':
    return '00:00', '24:00'
  open, close = (hour.strip() for hour in hours.split('-'))

  open_timeofday, open_am_or_pm = (part.lower() for part in open.split())
  open_hour, open_minute = (int(part) for part in open_timeofday.split(':'))
  open_time = datetime.time(open_hour, open_minute)
  if open_am_or_pm == 'pm':
    open_time = open_time.replace(hour=(open_time.hour + 12))

  close_timeofday, close_am_or_pm = (part.lower() for part in close.split())
  close_hour, close_minute = (int(part) for part in close_timeofday.split(':'))
  close_time = datetime.time(close_hour, close_minute)
  if close_am_or_pm == 'pm':
    close_time = close_time.replace(hour=(close_time.hour + 12))
  if close_time < open_time:
    return format_time(open_time.hour, open_time.minute), format_time(close_time.hour + 24, close_time.minute)
  return format_time(open_time.hour, open_time.minute), format_time(close_time.hour, close_time.minute)


def make_hours_id(db, hours_json):
  if hours_json is None:
    return None
  sun_open, sun_close = parse_day_hours(hours_json.get('Sun'))
  mon_open, mon_close = parse_day_hours(hours_json.get('Mon'))
  tue_open, tue_close = parse_day_hours(hours_json.get('Tue'))
  wed_open, wed_close = parse_day_hours(hours_json.get('Wed'))
  thu_open, thu_close = parse_day_hours(hours_json.get('Thu'))
  fri_open, fri_close = parse_day_hours(hours_json.get('Fri'))
  sat_open, sat_close = parse_day_hours(hours_json.get('Sat'))

  cursor = execute(db, """select id from StoreHours where
  sunday_open is ? and sunday_close is ? and
  monday_open is ? and monday_close is ? and
  tuesday_open is ? and tuesday_close is ? and
  wednesday_open is ? and wednesday_close is ? and
  thursday_open is ? and thursday_close is ? and
  friday_open is ? and friday_close is ? and
  saturday_open is ? and saturday_close is ?;
  """, (
  sun_open, sun_close,
  mon_open, mon_close,
  tue_open, tue_close,
  wed_open, wed_close,
  thu_open, thu_close,
  fri_open, fri_close,
  sat_open, sat_close))
  rows = list(cursor)
  if len(rows) > 0:
    (id,), = rows
    return id
  # We have to insert a row.
  cursor = execute(db, """insert into StoreHours(
  sunday_open, sunday_close,
  monday_open, monday_close,
  tuesday_open, tuesday_close,
  wednesday_open, wednesday_close,
  thursday_open, thursday_close,
  friday_open, friday_close,
  saturday_open, saturday_close)
  values (
    ?, ?,
    ?, ?,
    ?, ?,
    ?, ?,
    ?, ?,
    ?, ?,
    ?, ?);
  """, (
  sun_open, sun_close,
  mon_open, mon_close,
  tue_open, tue_close,
  wed_open, wed_close,
  thu_open, thu_close,
  fri_open, fri_close,
  sat_open, sat_close))

  rowid = cursor.lastrowid
  (id,), = execute(db, "select id from StoreHours where rowid = ?;", (rowid,))
  return id


def make_store_id(db, button):
  code = None
  name = None
  address = None
  url = None
  town = None
  state = None
  phone = None
  zip_code = None
  hours_json = None
  for key, value in button.attrs.items():
    # address and town are converted to title case (specifically,
    # `string.capwords(...)`), but name isn't.
    # I'm doing some partial canonicalization here.
    # For example, sometimes town is "Bronx" and sometimes it's "BRONX".
    # But I don't want to capitalize "of" in the name "Urban Market of Long Island City".
    if key == 'data-store':
      code = None if value == '' else int(value)
    elif key == 'data-name':
      name = value.strip()
    elif key == 'data-address':
      address = string.capwords(value.strip())
    elif key == 'data-site-url':
      url = value.strip()
    elif key == 'data-town':
      town = string.capwords(value.strip())
    elif key == 'data-region':
      state = value.strip().upper()
    elif key == 'data-phone':
      phone = value.strip()
      if phone == '':
        phone = None
    elif key == 'data-postal':
      zip_code = value.strip()
    elif key == 'data-hours':
      hours_json = None if value == '' else json.loads(value)
  if code is None:
    print('Button without a store code:', button, file=sys.stderr)
    return None
  # Marshal the store into the database.
  # First the address, then the URL, then the hours, and then the store.
  address_id = make_address_id(db, address, town, state, zip_code)
  url_id = make_url_id(db, url)
  hours_id = make_hours_id(db, hours_json)

  cursor = execute(db, """select id from ScrapedStore where
  code is ? and
  name is ? and
  phone is ? and
  address is ? and
  hours is ? and
  url is ?;
  """,
  (code, name, phone, address_id, hours_id, url_id))
  rows = list(cursor)
  if len(rows) > 0:
    (id,), = rows
    return id
  # We have to insert a row.
  cursor = execute(db, """insert into ScrapedStore(
  code,
  name,
  phone,
  address,
  hours,
  url) values (?, ?, ?, ?, ?, ?);
  """, (code, name, phone, address_id, hours_id, url_id))

  rowid = cursor.lastrowid
  (id,), = execute(db, "select id from ScrapedStore where rowid = ?;", (rowid,))
  return id


def main(db_path, input_file):
  db = sqlite3.connect(db_path)
  soup = BeautifulSoup(input_file, 'html.parser')
  buttons = soup.select('button.entry__session_button')
  for button in buttons:
    print('store row ID is', make_store_id(db, button))
    db.commit()


if __name__ == '__main__':
  main(db_path=sys.argv[1], input_file=sys.stdin)
