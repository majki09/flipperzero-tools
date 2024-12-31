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
