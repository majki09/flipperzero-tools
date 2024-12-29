import csv
import json.decoder
import jsonpickle
import keeloq
import logging
import os
import re
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
        self.datetime = None
        self.scan_place = None
        self.button = None
        self.counter = None
        self.gps_loc = None
        self.filename = ""

    @staticmethod
    def get_name_from_filename(filename:str):
        match = re.findall("\d{4}_\d{2}_\d{2}-\d{2}_\d{2}_\d{2,}", filename)

        if len(match) > 0:
            try:
                date_time = match[0]
                date = date_time.split('-')[0].replace("_", "-")
                time_wsufix = date_time.split('-')[1].replace("_", ":")

                return f"{date} {time_wsufix}"
            except:
                return None
        return None


class Database2:
    def __init__(self):
        self.keys = {}
        self.ignore_without_date = True

    def key_exists(self, key):
        return key["details"].serial_number in self.keys

    def add_key(self, key):
        # check if key has a valid datetime
        if self.ignore_without_date and key["subfile"].datetime is None:
            logger.info(f"Keyfile {key['subfile'].filename} has been ignored because it doesn't have a valid datetime.")
            return False

        # check if key already exists in database
        if self.key_exists(key):
            new_key = self.keys[key["details"].serial_number]
            logger.info(f"Key {new_key} loaded from database, it's already there.")

            occurrence = Occurrence.get_name_from_filename(key["subfile"].filename)
            # check if occurrence already exists
            if occurrence in new_key.occurrences:
                # new_occurrence = occurrence
                logger.info(f"Occurrence {occurrence} loaded from database, it's already there.")

                return True
            else:
                new_occurrence = self.add_occurrence_from_key(key)
        else:
            new_key = Key()
            new_key.serial_number = key["details"].serial_number

            new_occurrence = self.add_occurrence_from_key(key)

        new_key.occurrences.update({new_occurrence.datetime: new_occurrence})
        self.keys.update({new_key.serial_number: new_key})

    def add_occurrence_from_key(self, key):
        new_occurrence = Occurrence()
        new_occurrence.datetime = key["subfile"].datetime if not None else ""
        # new_occurrence.scan_place = ""
        new_occurrence.button = key["details"].button
        new_occurrence.filename = key["subfile"].filename

        return new_occurrence

    def update_scanplace_for_occurences(self, start_date: str, end_date: str, new_scanplace: str):
        for key in self.keys.values():
            for occurrence in key.occurrences.values():
                datetime_iso = datetime.fromisoformat(occurrence.datetime)
                if datetime.fromisoformat(start_date) < datetime_iso < datetime.fromisoformat(end_date):
                    if occurrence.scan_place != new_scanplace:
                        occurrence.scan_place = new_scanplace

    def save_to_file(self):
        jsonpickle.set_encoder_options("json", ensure_ascii=False)
        # self.update_scanplace_for_occurences("2024-05-28 07:30:00", "2024-05-28 07:31:00", "podleska")
        json_string = jsonpickle.encode(self.keys)
        with open("db2.json", "w", encoding="utf8") as file:
            file.write(json_string)

    def load_from_file(self):
        try:
            jsonpickle.set_decoder_options("json", encoding="utf8")
            with open("db2.json", "r", encoding="utf8") as file:
                self.keys = jsonpickle.decode(file.read())
        except json.decoder.JSONDecodeError:
            logger.error("Cannot load database from JSON file.")


class Database:
    key_template = {"datetime": None,
                    "serial_number": None,
                    "button": None,
                    "filename": None,
                    "notes": None}

    def __init__(self):
        self.output_file = "output/keeloqs.csv"
        self.rows = []
        self.keys = {}

        if self.check():
            self.get()
            self.keys = self.get_keys()

    def get(self):
        if not self.check():
            return 1
        else:
            with open(self.output_file, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) > 0:
                        self.rows.append(row)

    def get_keys(self):
        # key = self.key
        key = {}
        for row in self.rows:
            # key["datetime"] = row[0]
            key["serial_number"] = row[0]
            key["button"] = row[1]
            # key["filename"] = row[2]
            key["notes"] = row[2]
            self.keys.update({key["serial_number"]: key.copy()})

        return self.keys

    def check(self):
        return os.path.isfile(self.output_file)

    def create(self):
        pass

    def check_key(self, key):
        return key["details"].serial_number in self.keys

    def add(self, key):
        if not self.check_key(key):
            self.insert(key)
            logger.info(f"Key {key['details'].serial_number} has been added to database.")
        else:
            logger.debug(f"Key {key['details'].serial_number} already exist in the database.")

    # def insert(self, key):
    # with open(self.output_file, "a", newline='') as file:
    #     writer = csv.writer(file)
    #     writer.writerow([key["subfile"].datetime,
    #                      key["details"].serial_number,
    #                      key["details"].button,
    #                      key["subfile"].filename])

    def insert(self, key):
        new_key = {"datetime": key["subfile"].datetime if not None else "",
                   "serial_number": key["details"].serial_number,
                   "button": key["details"].button,
                   "filename": key["subfile"].filename,
                   "notes": ""
                   }
        self.keys.update({new_key["serial_number"]: new_key})

    def save_to_file(self):
        # fields = self.key_template.keys()
        with open(self.output_file, "w", newline="") as f:
            # w = csv.DictWriter(f, fields)
            # # w.writeheader()
            # for key in self.keys.values():
            #     w.writerow(key)

            writer = csv.writer(f)
            for key in self.keys.values():
                writer.writerow([key["serial_number"], key["button"], key["notes"]])


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
        self.database = Database()
        self.database2 = Database2()

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
                # self.database.add(subfile)

        return keys

    def process(self):
        self.database2.load_from_file()

        for key in self.keys:
            self.database.add(key)
            self.database2.add_key(key)
        self.log.add(self.keys)
        self.database.save_to_file()
        self.database2.save_to_file()

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
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.WARNING)

    logger = logging.getLogger("aggregator")

    aggr = Aggregator()
    aggr.process()
