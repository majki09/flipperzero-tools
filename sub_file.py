import re


class SubFile:
    def __init__(self, path: str):
        self.filename = path.split('/')[1]
        self.datetime = None
        self.file_object = None
        self.frequency = None
        self.preset = None
        self.protocol = None
        self.key = None
        self.manufacture = None

        self.load_file(path)
        self.parse_file()
        self.datetime = self.get_datetime()

    def load_file(self, path: str):
        with open(path, "r") as file:
            self.file_object = file.readlines()

    def parse_file(self):
        try:
            # for line in self.file_object:
            self.frequency = self.get_line("Frequency")
            self.key = self.get_line("Key:")
            self.preset = self.get_line("Preset")
            self.protocol = self.get_line("Protocol")
            self.manufacture = self.get_line("Manufacture")
        except:
            print("Error!")

    def get_line(self, parameter:str):
        for idx, line in enumerate(self.file_object):
            if parameter in line:
                return self.file_object[idx].split(":")[1].strip()

    def get_datetime(self):
        if len(re.findall("\d{4}_\d{2}_\d{2}-\d{2}_\d{2}_\d{2}", self.filename)) > 0:
            try:
                date_time = self.filename[-23:-4]
                date = date_time[:10].replace("_", "-")
                time = date_time[-8:].replace("_", ":")

                return f"{date} {time}"
            except:
                return None

