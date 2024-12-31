# SQLite Database

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
DROP TABLE occurences
CREATE TABLE occurences (
    button INTEGER,
    counter TEXT,
    date_time TEXT PRIMARY KEY,
    filename TEXT,
    gps_loc TEXT,
    remote TEXT,
    scan_place TEXT
)
```

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

### Occurences table
```python
self.con = sqlite3.connect("keeloqs.db")
cur = self.con.cursor()

for occu in key.occurrences.values():
    scan_place = "" if occu.scan_place is None else occu.scan_place
    counter = "" if occu.counter is None else occu.counter
    gps = "" if occu.gps_loc is None else occu.gps_loc
    print(occu.button, counter, occu.datetime, occu.filename, gps, key.serial_number, scan_place)
    cur.execute("INSERT INTO occurences VALUES (?, ?, ?, ?, ?, ?, ?)", [occu.button, counter, occu.datetime, occu.filename, gps, key.serial_number, scan_place])
```

## Tables joining
`SELECT remote FROM occurences INNER JOIN remotes ON remotes.serial_number = occurences.remote`
