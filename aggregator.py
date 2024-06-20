import csv
import logging
import keeloq
import os
import sub_file


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

            if not "Flipper SubGhz Key File" in subfile.file_object[0]:
                logger.warning(f"File \"{file}\" will not be processed. Invalid type.")
            else:
                files_objects.append(subfile)

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
        for key in self.keys:
            self.database.add(key)
        self.log.add(self.keys)
        self.database.save_to_file()

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
