class KeeloqKey:
    def __init__(self, key: str):
        self.key = key.replace(" ", "") if key else ""
        self.is_valid = self.validate()
        if not self.is_valid:
            self.second_part = 0
            self.inverted_binary = ""
            self.fixed = ""
            self.button = None
            self.serial_number = None
            return

        self.second_part = int(self.key[8:], 16)
        self.inverted_binary = self.invert_bits()
        self.fixed = self.inverted_to_hex(self.inverted_binary)
        self.button = self.fixed[2]
        self.serial_number = self.fixed[3:].upper()

    def validate(self):
        if len(self.key) != 16:
            return False
        try:
            int(self.key, 16)
            return True
        except ValueError:
            return False

    def invert_bits(self):
        binary = bin(self.second_part)[2:].zfill(32)
        return binary[::-1]

    def inverted_to_hex(self, inverted):
        return f"{int(inverted, 2):#010x}"
