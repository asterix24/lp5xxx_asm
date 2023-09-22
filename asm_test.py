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
        pass

if __name__ == '__main__':
    unittest.main()
