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
            # logger.info(f"Key {new_key} already in database, skipping.")

            occurrence = Occurrence.get_name_from_filename(key["subfile"].filename)
            # check if occurrence already exists
            if occurrence in new_key.occurrences:
                # new_occurrence = occurrence
                # logger.info(f"Occurrence \"{occurrence}\" already in database, skipping.")

                return True
            else:
                new_occurrence = self.add_occurrence_from_key(key)
                logger.info(
                    f"New occurrence \"{new_occurrence.datetime}\" for existing key {new_key.serial_number} from file {new_occurrence.filename} added.")
        else:
            new_key = Key()
            new_key.serial_number = key["details"].serial_number
            logger.info(f"New key {new_key.serial_number} from file {key['subfile'].filename} added.")

            new_occurrence = self.add_occurrence_from_key(key)
            logger.info(
                f"New occurrence \"{new_occurrence.datetime}\" for key {new_key.serial_number} from file {key['subfile'].filename} added.")

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

    def convert_to_sqlite(self, con):
        cur = con.cursor()
        for key in self.keys.values():
            for occu in key.occurrences.values():
                try:
                    scan_place = "" if occu.scan_place is None else occu.scan_place
                    counter = "" if occu.counter is None else occu.counter
                    gps = "" if occu.gps_loc is None else occu.gps_loc
                    print(occu.button, counter, occu.datetime, occu.filename, gps, key.serial_number, scan_place)
                    cur.execute("INSERT INTO occurences VALUES (?, ?, ?, ?, ?, ?, ?)",
                                [occu.button, counter, occu.datetime, occu.filename, gps, key.serial_number,
                                 scan_place])
                except sqlite3.IntegrityError as IE:
                    print(IE)
        con.commit()

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
