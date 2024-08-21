"""re_match - sqlite3 regular expression pattern extraction function

TODO
"""
import json
import re
import sqlite3
import sys


def matcher_func(flags=0):
  def func(pattern, subject, *more):
    replacement = None
    if len(more) > 0:
      replacement, = more
    match = re.fullmatch(pattern, subject, flags)
    if match is None:
      return None
    if replacement is None:
      if len(match.groups()) == 0:
        return subject
      replacement = r'\g<1>'
    return re.sub(pattern, replacement, subject, flags=flags)
  return func


def main(db_path, input_file):
  db = sqlite3.connect(db_path)
  db.create_function('re_match', -1, matcher_func(), deterministic=True)
  db.create_function('re_matchi', -1, matcher_func(re.IGNORECASE), deterministic=True)

  cursor = db.execute(input_file.read())
  for row in cursor:
    print(json.dumps(row))


if __name__ == '__main__':
  main(sys.argv[1], sys.stdin)
