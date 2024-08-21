import datetime
import sqlite3
import sys


def usage(file):
    print(f'usage: {sys.argv[0]} <sqlite database file path> <store ID>', file=file)


if __name__ == '__main__':
  if len(sys.argv) != 3:
    usage(sys.stderr)
    sys.exit(1)

  store_id = int(sys.argv[2])

  with sqlite3.connect(sys.argv[1]) as db:
    cursor = db.execute("""
    insert into ScrapeSession(when_begin_iso, store)
    values(?, ?);
    """, (datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
      store_id))
    rowid = cursor.lastrowid

    (session_id,), = db.execute("""
    select id from ScrapeSession where rowid = ?;
    """, (rowid,))

    print(session_id)
