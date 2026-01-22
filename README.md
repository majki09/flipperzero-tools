# Flipper Zero KeeLoq Tools

Collects KeeLoq SubGhz keys from Flipper `.sub` files and stores them in a SQLite database.

## Usage
1. Create an `input` folder next to this README.
2. Put your `.sub` files in `input`.
3. Run `aggregator.py` (it writes to `keeloqs.db`).

The logger writes to `log.log` when running the script directly.

## Input expectations
- Only `.sub` files are processed.
- Files must be Flipper SubGhz key files (first line contains `Flipper SubGhz Key File`).
- Only `Protocol: KeeLoq` files are parsed.
- If a filename does not include a parseable datetime, it may be skipped depending on configuration.

## Tables creating
```sqlite-sql
DROP TABLE remotes
CREATE TABLE remotes (
  serial_number TEXT PRIMARY KEY,
  notes TEXT,
  tags TEXT
)
```
```sqlite-sql
DROP TABLE occurrences
CREATE TABLE occurrences (
    button INTEGER,
    counter TEXT,
    date_time TEXT PRIMARY KEY,
    filename TEXT,
    gps_loc TEXT,
    remote TEXT,
    scan_place TEXT
)
```

Notes:
- `date_time` is derived from the filename (see `Occurrence.get_name_from_filename()`).
- `occurrences` is the current table name used in code.

## Convert dict to SQLite database
### Remotes table
```python
self.con = sqlite3.connect("keeloqs.db")
cur = self.con.cursor()

for key in self.database2.keys.values():
    note = "" if key.note is None else key.note
    tags = ", ".join(key.tags) if len(key.tags)>0 else None
    cur.execute("INSERT INTO remotes VALUES (?, ?, ?)", [key.serial_number, note, tags])
```

### Occurrences table
```python
self.con = sqlite3.connect("keeloqs.db")
cur = self.con.cursor()

for occu in key.occurrences.values():
    scan_place = "" if occu.scan_place is None else occu.scan_place
    counter = "" if occu.counter is None else occu.counter
    gps = "" if occu.gps_loc is None else occu.gps_loc
    print(occu.button, counter, occu.datetime, occu.filename, gps, key.serial_number, scan_place)
    cur.execute("INSERT INTO occurrences VALUES (?, ?, ?, ?, ?, ?, ?)", [occu.button, counter, occu.datetime, occu.filename, gps, key.serial_number, scan_place])
```

## Tables joining
`SELECT remote FROM occurrences INNER JOIN remotes ON remotes.serial_number = occurrences.remote`
