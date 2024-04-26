import csv
import keeloq
import os
import sub_file


class Database:
    def __init__(self):
        self.output_file = "output/keeloqs.csv"
        self.rows = []
        self.keys = []

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
        keys = []
        for row in self.rows:
            keys.append(row[1])

        return keys

    def check(self):
        return os.path.isfile(self.output_file)

    def create(self):
        pass

    def check_key(self, key):
        return key["details"].serial_number in self.keys

    def add(self, key):
        if not self.check_key(key):
            self.insert(key)
        else:
            print(f"Key {key['details'].serial_number} already exist in the database.")

    def insert(self, key):
        with open(self.output_file, "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([key["subfile"].datetime,
                             key["details"].serial_number,
                             key["details"].button,
                             key["subfile"].filename])


class Aggregator:
    def __init__(self):
        self.input_dir = "input"
        self.sub_files = []
        self.database = Database()
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
                print("This file will not be processed. Wrong type.")
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
            # key = keeloq.KeeloqKey(subfile.key)
            #
            # print(f"SN: {key.serial_number}, button: {key.button}")
            self.database.add(key)


if __name__ == '__main__':
    aggr = Aggregator()
    aggr.process()

    # for file in sub_files:
    #
    #     subfile = sub_file.SubFile(self.input_dir + "/" + file)
