import json
import sqlite3
import sys
import traceback


def usage(file):
    print(f'usage: {sys.argv[0]} <sqlite database file path> <scrape session ID>', file=file)


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

  with sqlite3.connect(sys.argv[1]) as db:
    for line in sys.stdin:
      try:
        product = json.loads(line)
        db.execute("""
        insert or ignore into ScrapedCatalogEntry(
          scrape_session,
          name,
          size,
          price,
          cart_code,
          product_page_path)
        values (?, ?, ?, ?, ?, ?);
        """, (
          scrape_session,
          product.get('name'),
          product.get('size'),
          product.get('price'),
          product.get('cart_code'),
          product.get('product_page_path')))
      except Exception:
        traceback.print_exc()
