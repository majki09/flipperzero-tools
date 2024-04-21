# import leekoq
import math


# key = 0xCAFEDEAD
# cipher = leekoq.encrypt(0xea89e403, key)
# print(hex(cipher))
# plain = leekoq.decrypt(cipher, key)
# print(hex(plain))


class KeyloqKey:
    def __init__(self, key: str):
        self.key = key.replace(" ", "")
        self.is_valid = self.validate()
        self.second_part = int(self.key[8:], 16)
        self.inverted_binary = self.invert_bits()
        self.fixed = self.inverted_to_hex()
        self.button = self.fixed[2]
        self.serial_number = self.fixed[3:].upper()

    def validate(self):
        return len(self.key) == 16

    def invert_bits(self):
        binary = bin(self.second_part)[2:].zfill(32)
        return binary[::-1]

    def inverted_to_hex(self):
        return hex(int(self.inverted_binary, 2))


if __name__ == '__main__':
    key = KeyloqKey("c0 2f 91 57 2a 68 f3 14")

    print(f"Fixed for \"{key.key}\" = {key.fixed}")
