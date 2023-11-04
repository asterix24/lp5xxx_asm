import unittest
import lp5xxx_asm
import logging
import tracemalloc
import os


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
    "all": "09",
    "loop1": "10"
}

class TestASM(unittest.TestCase):
    def setUp(self):
        tracemalloc.start()
        logging.basicConfig(level=logging.ERROR)

    def __dotest(self, src_name, chk_bin):
        with open(src_name) as src:
            memory, labels = lp5xxx_asm.parse(src, logging)
            asm_bin = lp5xxx_asm.asm(labels, memory, logging)

            for n, i in enumerate(chk_bin):
                self.assertEqual(i, asm_bin[n], f"Missmatch [{i}] {i:02x} != {asm_bin[n]:02x}")


    def test_labels(self):
        src_name = os.path.join(".", "src", "labels.src")
        with open(src_name) as src:
            memory, labels = lp5xxx_asm.parse(src, logging)
            for m in chk_labels:
                self.assertEqual(f"{labels[m]:02X}", chk_labels[m], f"label missmatch [{m}]")

    def test_bin(self):
        chk_bin = [
            0x00, 0x01, 0x00, 0x02, 0x00, 0x04, 0x00, 0x08, 0x00, 0x10, 0x00, 0x20, 0x00, 0x40, 0x00, 0x80,
            0x01, 0x00, 0x01, 0xff, 0x9f, 0x89, 0x28, 0x64, 0x29, 0x64, 0x5a, 0x00, 0x9c, 0x00, 0x9c, 0x88,
            0x40, 0x00, 0x9d, 0x80, 0x40, 0x05, 0x9d, 0x80, 0x40, 0x14, 0x9d, 0x80, 0x40, 0x50, 0x9d, 0xc0,
            0x9d, 0xc0, 0x48, 0x00, 0xa0, 0x06, 0xc0, 0x00, 0xc0, 0x00, 0xc0, 0x00, 0x00, 0x00, 0x00, 0x00,
        ]
        self.__dotest(os.path.join(".", "src", "labels.src"), chk_bin)

    def test_bin2(self):
        chk_bin = [
            0x00, 0x01, 0x00, 0x02, 0x00, 0x04, 0x00, 0x38, 0x01, 0xC0, 0x9C, 0x00, 0x9C, 0x84, 0x28, 0xC8,
            0x21, 0xFF, 0x74, 0x00, 0x9D, 0x80, 0xA2, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        ]
        self.__dotest(os.path.join(".", "src", "test.src"), chk_bin)

    def test_bin3(self):
        chk_bin = [
            0x00, 0x01, 0x00, 0x02, 0x00, 0x04, 0x00, 0x08, 0x00, 0x10, 0x00, 0x20, 0x00, 0x40, 0x00, 0x80,
            0x01, 0x00, 0x01, 0xFF, 0x9F, 0x89, 0x28, 0x64, 0x29, 0x64, 0x5A, 0x00, 0x9C, 0x04, 0x9C, 0x88,
            0x40, 0x00, 0x9D, 0x80, 0x40, 0x05, 0x9D, 0x80, 0x40, 0x14, 0x9D, 0x80, 0x40, 0x50, 0x9D, 0xC0,
            0x9D, 0xC0, 0x48, 0x00, 0xA0, 0x06, 0xC0, 0x00, 0x9F, 0x80, 0x28, 0x64, 0x29, 0x64, 0x9F, 0x81,
            0x28, 0x64, 0x29, 0x64, 0x9F, 0x83, 0x28, 0x64, 0x29, 0x64, 0x9C, 0x00, 0x9C, 0x83, 0x40, 0x00,
            0x9D, 0x80, 0x40, 0x05, 0x9D, 0x80, 0x40, 0x14, 0x9D, 0x80, 0x40, 0x50, 0x9D, 0xC0, 0x9D, 0xC0,
            0x48, 0x00, 0xA0, 0x0B, 0xC0, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        ]
        self.__dotest(os.path.join(".", "src", "test1.src"), chk_bin)

    def test_bin4(self):
        chk_bin = [
            0x01, 0xFF, 0x9F, 0x80, 0x28, 0x64, 0x14, 0x64, 0x84, 0x06, 0x31, 0xFB, 0x84, 0x38, 0xC0, 0x00,
            0x84, 0x61, 0xC0, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ]
        self.__dotest(os.path.join(".", "src", "ramp.src"), chk_bin)

    def test_bin5(self):
        chk_bin = [
            0x00, 0x01, 0x00, 0x02, 0x00, 0x04, 0x00, 0x08, 0x00, 0x10, 0x00, 0x20, 0x00, 0x40, 0x00, 0x80,
            0x01, 0x00, 0x01, 0xFF, 0xE0, 0x80, 0xF3, 0xCE, 0xC0, 0x00, 0xE0, 0x02, 0xF3, 0x02, 0xC0, 0x00,
            0xE0, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ]
        self.__dotest(os.path.join(".", "src", "trigger.src"), chk_bin)

    def test_bin6(self):
        chk_bin = [
            0x00, 0x01, 0x00, 0x02, 0x00, 0x04, 0x00, 0x08, 0x00, 0x10, 0x00, 0x20, 0x00, 0x40, 0x00, 0x80,
            0x01, 0x00, 0x01, 0xFF, 0x40, 0xF0, 0x8E, 0x00, 0x40, 0xFA, 0xC0, 0x00, 0x40, 0xFD, 0x8C, 0x2B,
            0x8A, 0x14, 0x88, 0x0D, 0x40, 0xF4, 0xC0, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ]
        self.__dotest(os.path.join(".", "src", "jump.src"), chk_bin)

    def test_bin7(self):
        chk_bin = [
            0x00, 0x01, 0x00, 0x02, 0x00, 0x04, 0x00, 0x08, 0x00, 0x10, 0x00, 0x20, 0x00, 0x40, 0x00, 0x80,
            0x01, 0x00, 0x01, 0xFF, 0x40, 0xF0, 0x93, 0x0E, 0x97, 0x11, 0x98, 0x19, 0x40, 0xFA, 0xC0, 0x00,
            0x40, 0xFD, 0x91, 0x13, 0x96, 0x53, 0x40, 0xF4, 0xC0, 0x00, 0x93, 0x00, 0xC0, 0x00, 0x00, 0x00
        ]
        self.__dotest(os.path.join(".", "src", "alu.src"), chk_bin)

    def test_bin8(self):
        chk_bin = [
            0x00, 0x01, 0x00, 0x08, 0x00, 0x40, 0x00, 0x02, 0x00, 0x10, 0x00, 0x80, 0x00, 0x04, 0x00, 0x20,
            0x01, 0x00, 0x01, 0xFF, 0x9F, 0x89, 0x28, 0x64, 0x29, 0x64, 0x5A, 0x00, 0x9C, 0x06, 0x9C, 0x88,
            0xE0, 0x02, 0xC0, 0x00, 0xE0, 0x80, 0x40, 0x00, 0x9D, 0x80, 0x4C, 0x00, 0x40, 0x0F, 0x9D, 0x80,
            0x4C, 0x00, 0x40, 0x00, 0x9D, 0x80, 0x4C, 0x00, 0x9D, 0xC0, 0x66, 0x00, 0xA1, 0x81, 0xC0, 0x00
        ]
        self.__dotest(os.path.join(".", "src", "test2.src"), chk_bin)

    def test_deasm0(self):
        bin = [
            0x00, 0x01, 0x00, 0x08, 0x00, 0x40, 0x00, 0x02, 0x00, 0x10, 0x00, 0x80, 0x00, 0x04, 0x00, 0x20,
            0x01, 0x00, 0x01, 0xFF, 0x9F, 0x89, 0x28, 0x64, 0x29, 0x64, 0x5A, 0x00, 0x9C, 0x06, 0x9C, 0x88,
            0xE0, 0x02, 0xC0, 0x00, 0xE0, 0x80, 0x40, 0x00, 0x9D, 0x80, 0x4C, 0x00, 0x40, 0x0F, 0x9D, 0x80,
            0x4C, 0x00, 0x40, 0x00, 0x9D, 0x80, 0x4C, 0x00, 0x9D, 0xC0, 0x66, 0x00, 0xA1, 0x81, 0xC0, 0x00
        ]

        addr = [0x0A, 0x12, 0x20]

        #src = open(os.path.join(".", "src", "test2.src"))
        #memory, labels = lp5xxx_asm.parse(src, logging)
        #asm_bin = lp5xxx_asm.asm(labels, memory, logging)
        lp5xxx_asm.deasm(bin, addr, logging)
        print(memory, labels)

    def test_deasm1(self):
        bin = [
            0x00, 0x01, 0x00, 0x02, 0x00, 0x04, 0x00, 0x08, 0x00, 0x10, 0x00, 0x20, 0x00, 0x40, 0x00, 0x80,
            0x01, 0x00, 0x01, 0xFF, 0x40, 0xF0, 0x93, 0x0E, 0x97, 0x11, 0x98, 0x19, 0x40, 0xFA, 0xC0, 0x00,
            0x40, 0xFD, 0x91, 0x13, 0x96, 0x53, 0x40, 0xF4, 0xC0, 0x00, 0x93, 0x00, 0xC0, 0x00, 0x00, 0x00
        ]

        addr = [0x0A, 0x10, 0x15]

        #self.__dotest(os.path.join(".", "src", "alu.src"), chk_bin)
        lp5xxx_asm.deasm(bin, addr, logging)
        print(memory, labels)

    def test_deasm2(self):
        bin = [
            0x00, 0x01, 0x00, 0x02, 0x00, 0x04, 0x00, 0x08, 0x00, 0x10, 0x00, 0x20, 0x00, 0x40, 0x00, 0x80,
            0x01, 0x00, 0x01, 0xFF, 0x9F, 0x89, 0x28, 0x64, 0x29, 0x64, 0x5A, 0x00, 0x9C, 0x04, 0x9C, 0x88,
            0x40, 0x00, 0x9D, 0x80, 0x40, 0x05, 0x9D, 0x80, 0x40, 0x14, 0x9D, 0x80, 0x40, 0x50, 0x9D, 0xC0,
            0x9D, 0xC0, 0x48, 0x00, 0xA0, 0x06, 0xC0, 0x00, 0x9F, 0x80, 0x28, 0x64, 0x29, 0x64, 0x9F, 0x81,
            0x28, 0x64, 0x29, 0x64, 0x9F, 0x83, 0x28, 0x64, 0x29, 0x64, 0x9C, 0x00, 0x9C, 0x83, 0x40, 0x00,
            0x9D, 0x80, 0x40, 0x05, 0x9D, 0x80, 0x40, 0x14, 0x9D, 0x80, 0x40, 0x50, 0x9D, 0xC0, 0x9D, 0xC0,
            0x48, 0x00, 0xA0, 0x0B, 0xC0, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        ]

        addr = [0x0A, 0x1C, 0x33]
        #self.__dotest(os.path.join(".", "src", "test1.src"), chk_bin)
        lp5xxx_asm.deasm(bin, addr, logging)
        print(memory, labels)


if __name__ == '__main__':
    unittest.main()
