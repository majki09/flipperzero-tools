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

        self.file_object = self.load_file(path)
        self.parse_file()
        self.datetime = self.get_datetime()

    def load_file(self, path: str):
        with open(path, "r") as file:
            return file.readlines()

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
        # dates with _
        match = re.findall("\d{4}_\d{2}_\d{2}-\d{2}_\d{2}_\d{2}", self.filename)
        if len(match) > 0:
            try:
                date_time = match[0]
                date = date_time.split('-')[0].replace("_", "-")
                time = date_time.split('-')[1].replace("_", ":")

                return f"{date} {time}"
            except:
                return None

        # dates without _
        match = re.findall("-\d{4}\d{2}\d{2}-\d{2}\d{2}\d{2}", self.filename)
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

