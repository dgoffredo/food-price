import datetime
from pathlib import Path
import sqlite3
import sys
import traceback


def usage(file):
    print(f'usage: {sys.argv[0]} <sqlite database file path> <scrape session ID>', file=file)


def content_or_none(path):
  try:
    if path.exists():
      return path.read_text()
  except Exception:
    traceback.print_exc()


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
    # Assume that the log files, if they exist, are in the current directory.
    cursor = db.execute("""
    insert into ScrapeSessionLog(
      scrape_status, scrape_stderr,
      parse_status, parse_stderr,
      persist_status, persist_stderr)
    values (?, ?, ?, ?, ?, ?);
    """, (
      content_or_none(Path('scrape.status')),
      content_or_none(Path('scrape.stderr')),
      content_or_none(Path('parse.status')),
      content_or_none(Path('parse.stderr')),
      content_or_none(Path('persist.status')),
      content_or_none(Path('persist.stderr'))))

    rowid = cursor.lastrowid
    (log_id,), = db.execute("""
    select id from ScrapeSessionLog where rowid = ?;
    """, (rowid,))

    db.execute("""
    update ScrapeSession set log = ?, when_end_iso = ? where id = ?;
    """, (
      log_id,
      datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
      scrape_session))
