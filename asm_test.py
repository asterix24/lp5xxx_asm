import unittest
import lp55xx_asm
import os

src_name = os.path.join(".", "src", "isokey.src")

memory = []
labels = {}
chk_labels = {
    "m0": "00",
    "m1": "01",
    "m2": "02",
    "m3": "03",
    "m4": "04",
    "m5": "05",
    "m6": "06",
    "m7": "07",
    "m8": "08",
    "all":"09",
    "loop1": "10"
}

class TestASM(unittest.TestCase):
    def setUp(self):
        pass

    def test_labels(self):
        src = open(src_name)
        memory, labels = lp55xx_asm.parse(src)
        for m in chk_labels:
            self.assertEqual(f"{labels[m]:02X}", chk_labels[m], f"label missmatch [{m}]")

    def test_bin(self):
        chk_bin = [
            0x00,0x01,0x00,0x02,0x00,0x04,0x00,0x08,0x00,0x10,0x00,0x20,0x00,0x40,0x00,0x80,
            0x01,0x00,0x01,0xff,0x9f,0x89,0x28,0x64,0x29,0x64,0x5a,0x00,0x9c,0x00,0x9c,0x88,
            0x40,0x00,0x9d,0x80,0x40,0x05,0x9d,0x80,0x40,0x14,0x9d,0x80,0x40,0x50,0x9d,0xc0,
            0x9d,0xc0,0x48,0x00,0xa0,0x06,0xc0,0x00,0xc0,0x00,0xc0,0x00,0x00,0x00,0x00,0x00,
        ]
        src = open(src_name)
        memory, labels = lp55xx_asm.parse(src)
        asm_bin = lp55xx_asm.asm(labels, memory)
        for n, i in enumerate(chk_bin):
            self.assertEqual(f"0x{i:02x}", asm_bin[n], f"Missmatch [{i}]")


if __name__ == '__main__':
    unittest.main()
