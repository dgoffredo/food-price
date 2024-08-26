import json
import sqlite3
import sys
import traceback


def usage(file):
    print(f'usage: {sys.argv[0]} <sqlite database file path> <scrape session ID>', file=file)


def execute(db, query, params):
    # print(query, params)
    return db.execute(query, params)
    

if __name__ == '__main__':
  if len(sys.argv) != 3:
    usage(sys.stderr)
    sys.exit(1)
  try:
    scrape_session = int(sys.argv[2])
  except Exception:
    traceback.print_exc()
    print(file=sys.stderr)
    usage(sys.stderr)
    sys.exit(2)

  db = sqlite3.connect(sys.argv[1])
  for line in sys.stdin:
    try:
      product = json.loads(line)
      with db:
        name = product.get('name')
        # If `name` is absent, then we can just use null for the entry's
        # foreign key into the table of names.
        # If `name` is present, then we have to find or insert the
        # corresponding row in the table of names.
        if name is not None:
          # Convert the `name` string into an ID (integer).
          #
          # We could use `insert or ignore into ScrapedCatalogEntryName`,
          # except that I forgot to add a `unique` constraint to the `name`
          # column. Due to foreign keys, it's hard to fix it now.
          # Instead, enforce the uniqueness of names manually.
          rows = list(execute(db, """
          select id from ScrapedCatalogEntryName where name = ?;
          """, (name,)))
          if len(rows) == 1:
            (name,), = rows
          else:
            cursor = execute(db, """
            insert into ScrapedCatalogEntryName(name) values(?);
            """, (name,))
            name = cursor.lastrowid

        # The `code` is something like a UPC code. If the product has a
        # "cart_code", then that's it. Otherwise, and more often, it's the last
        # part of the "product_page_path".
        # If none of that works, then it's null.
        cart_code = product.get('cart_code', '')
        path = product.get('product_page_path', '')
        if cart_code:
          code = cart_code
        elif path:
          try:
            code = path.split('/')[-1]
          except Exception:
            code = None
        else:
          code = None

        execute(db, """
        insert or ignore into ScrapedCatalogEntry(
          scrape_session,
          code,
          name,
          size,
          price)
        values (?, ?, ?, ?, ?);
        """, (
          scrape_session,
          code,
          name,
          product.get('size'),
          product.get('price')))
    except Exception:
      traceback.print_exc()

