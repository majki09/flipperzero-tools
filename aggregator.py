import csv
import keeloq
import logging
import os
import re
import sqlite3
import sub_file

from datetime import datetime


class Key:
    def __init__(self):
        self.serial_number = None
        self.occurrences = {}
        self.note = None
        self.tags = []


class Occurrence:
    def __init__(self):
        self.name = ""
        self.datetime = None
        self.scan_place = None
        self.button = None
        self.counter = None
        self.gps_loc = None
        self.filename = ""

    @staticmethod
    def get_name_from_filename(filename: str):
        # dates with _
        match = re.findall("\d{4}_\d{2}_\d{2}-\d{2}_\d{2}_\d{2,}", filename)

        if len(match) > 0:
            try:
                date_time = match[0]
                date = date_time.split('-')[0].replace("_", "-")
                time_wsufix = date_time.split('-')[1].replace("_", ":")

                return f"{date} {time_wsufix}"
            except:
                return None

        # dates without _
        match = re.findall("-\d{4}\d{2}\d{2}-\d{2}\d{2}\d{2,}", filename)
        if len(match) > 0:
            try:
                date_time = match[0][1:]
                date, time = date_time.split('-')
                date = date[:4] + '-' + date[4:]
                date = date[:7] + '-' + date[7:]
                time = time[:2] + ':' + time[2:]
                time = time[:5] + ':' + time[5:]

                return f"{date} {time}"
            except:
                return None

        return None


class SQLiteDatabase:
    def __init__(self, db_file):
        self.db_file = db_file
        self.con = sqlite3.connect(self.db_file)
        self.cur = self.con.cursor()
        self.remotes = {}
        self.ignore_without_date = True

    def key_exists(self, key):
        return key["details"].serial_number in self.remotes

    def add_key(self, key):
        # check if key has a valid datetime
        if self.ignore_without_date and key["subfile"].datetime is None:
            logger.info(f"Keyfile \"{key['subfile'].filename}\" has been ignored because it doesn't have a valid datetime.")
            return False

        # check if key already exists in database
        if self.key_exists(key):
            new_key = self.remotes[key["details"].serial_number]
            # logger.info(f"Key {new_key} already in database, skipping.")

            # check if occurrence already exists
            occurrence = Occurrence.get_name_from_filename(key["subfile"].filename)
            if occurrence in new_key.occurrences:
                # new_occurrence = occurrence
                # logger.info(f"Occurrence \"{occurrence}\" already in database, skipping.")

                return True
            else:
                new_occurrence = self.add_occurrence_from_key(key)
                if new_occurrence.name is None:
                    logger.info(f"Occurrence \"{key['subfile'].filename}\" has been ignored because could not get a valid datetime.")
                    return False

                logger.info(
                    f"New occurrence \"{new_occurrence.name}\" for existing key {new_key.serial_number} from file {new_occurrence.filename} added.")
        else:
            # adding new KEY
            new_key = Key()
            new_key.serial_number = key["details"].serial_number

            note = "" if new_key.note is None else new_key.note
            tags = ", ".join(new_key.tags) if len(new_key.tags) > 0 else None
            self.cur.execute("INSERT INTO remotes VALUES (?, ?, ?)", [new_key.serial_number, note, tags])
            self.con.commit()

            logger.info(f"New key {new_key.serial_number} from file {key['subfile'].filename} added.")

            # adding new OCCURRENCE
            new_occurrence = self.add_occurrence_from_key(key)
            if new_occurrence.name is None:
                logger.info(f"Occurrence \"{key['subfile'].filename}\" has been ignored because could not get a valid datetime.")
                return False
            logger.info(
                f"New occurrence \"{new_occurrence.name}\" for NEW key {new_key.serial_number} from file {key['subfile'].filename} added.")

        new_key.occurrences.update({new_occurrence.datetime: new_occurrence})
        self.remotes.update({new_key.serial_number: new_key})

    def add_occurrence_from_key(self, key):
        new_occurrence = Occurrence()
        new_occurrence.datetime = "" if key["subfile"].datetime is None else key["subfile"].datetime
        # new_occurrence.scan_place = ""
        new_occurrence.button = key["details"].button
        new_occurrence.filename = key["subfile"].filename
        new_occurrence.name = new_occurrence.get_name_from_filename(new_occurrence.filename)

        # add to SQLite
        scan_place = "" if new_occurrence.scan_place is None else new_occurrence.scan_place
        counter = "" if new_occurrence.counter is None else new_occurrence.counter
        gps = "" if new_occurrence.gps_loc is None else new_occurrence.gps_loc
        # print(new_occurrence.button, counter, new_occurrence.datetime, new_occurrence.filename, gps, key.serial_number, scan_place)
        try:
            self.cur.execute("INSERT INTO occurences VALUES (?, ?, ?, ?, ?, ?, ?)",
                        [new_occurrence.button,
                         counter,
                         new_occurrence.name,
                         new_occurrence.filename,
                         gps,
                         key["details"].serial_number,
                         scan_place])
            self.con.commit()
        except sqlite3.IntegrityError:
            logger.error(f"Could not INSERT {new_occurrence.filename} into SQLite database!")

        return new_occurrence

    def update_scanplace_for_occurences(self, start_date: str, end_date: str, new_scanplace: str):
        for key in self.remotes.values():
            for occurrence in key.occurrences.values():
                datetime_iso = datetime.fromisoformat(occurrence.datetime)
                if datetime.fromisoformat(start_date) < datetime_iso < datetime.fromisoformat(end_date):
                    if occurrence.scan_place != new_scanplace:
                        occurrence.scan_place = new_scanplace

    def load_from_file(self):
        self.get_remotes()
        self.get_occurrences()

    def get_remotes(self):
        self.cur.execute("SELECT * FROM remotes")
        rows = self.cur.fetchall()
        for row in rows:
            loaded_key = Key()
            loaded_key.serial_number, loaded_key.note, loaded_key.tags = row
            self.remotes.update({loaded_key.serial_number: loaded_key})

        logger.info(f"\"remotes\" table from SQLite database loaded with {len(rows)} rows.")

    def get_occurrences(self):
        self.cur.execute("SELECT * FROM occurences")
        rows = self.cur.fetchall()
        for row in rows:
            loaded_occu = Occurrence()
            loaded_occu.button, loaded_occu.counter, loaded_occu.datetime, loaded_occu.filename, loaded_occu.gps_loc,\
              remote_sn, loaded_occu.scan_place = row
            self.remotes[remote_sn].occurrences.update({loaded_occu.datetime: loaded_occu})

        logger.info(f"\"occurrences\" table from SQLite database loaded with {len(rows)} rows.")

class Log:
    key_template = {"datetime": None,
                    "serial_number": None,
                    "button": None,
                    "filename": None,
                    "notes": None}

    def __init__(self):
        self.output_file = "output/logs.csv"
        self.keys = {}

    def add(self, keys):
        fields = self.key_template.keys()
        for key in keys:
            if key["subfile"].datetime is not None:
                new_key = {"datetime": key["subfile"].datetime if not None else "",
                           "serial_number": key["details"].serial_number,
                           "button": key["details"].button,
                           "filename": key["subfile"].filename,
                           "notes": ""
                           }
                self.keys.update({new_key["datetime"]: new_key})

        with open(self.output_file, "w", newline="") as f:
            w = csv.DictWriter(f, fields)
            w.writeheader()
            for key in self.keys.values():
                w.writerow(key)


class Aggregator:
    def __init__(self):
        self.input_dir = "input"
        self.sub_files = []
        self.sql_db = SQLiteDatabase("keeloqs.db")
        # logger.info("keeloqs.db SQLite database loaded.")

        self.log = Log()
        self.keys = []

        # import input files
        self.sub_files = self.get_input_files()
        self.keys = self.keys_collect(self.sub_files)

    def get_input_files(self):
        files = [file for file in os.listdir(self.input_dir) if file.split(".")[1] == "sub"]

        files_objects = []
        for file in files:
            subfile = sub_file.SubFile(self.input_dir + "/" + file)

            # check if subfile is not empty
            if len(subfile.file_object) > 0:
                if not "Flipper SubGhz Key File" in subfile.file_object[0]:
                    logger.warning(f"File \"{file}\" will not be processed. Invalid type.")
                else:
                    files_objects.append(subfile)
            else:
                logger.warning(f"File {file} is empty, ignoring.")

        return files_objects

    def keys_collect(self, sub_files_list: list):
        keys = []
        for subfile in sub_files_list:
            if subfile.protocol == "KeeLoq":
                key = {}
                key["subfile"] = subfile
                key["details"] = keeloq.KeeloqKey(subfile.key)
                keys.append(key)
                # print(f"SN: {key.serial_number}, button: {key.button}")

        return keys

    def process(self):
        self.sql_db.load_from_file()

        for index, key in enumerate(self.keys):
            print(f'{index}/{len(self.keys)}\t{index / len(self.keys) * 100:.0f}%\tProcessing remote {key["details"].serial_number} '
                        f'({key["subfile"].filename})')
            self.sql_db.add_key(key)
        # self.log.add(self.keys)

    def find_key(self, filename: str):
        """
        Finds key that is coming from given filename.

        Example:
        awe = next(a for a in aggr.keys if "awe" in a["subfile"].filename)

        :param filename:
        :return:
        """
        return next(a for a in aggr.keys if filename in a["subfile"].filename)


if __name__ == '__main__':
    logging.basicConfig(filename="log.log",
                        filemode="a",
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    logger = logging.getLogger("aggregator")

    aggr = Aggregator()
    aggr.process()
