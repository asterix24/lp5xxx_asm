#!/bin/env python

import re
instruction_set = {
    "dw":{"min":0b0, "max":0b0000000111111111},
    "map_start":{"op":0},
    "load_end":{"op":0},
    "map_addr":{"op":0b100111111, "args_bits":6},
    "map_next":{"op":0},
    "map_prev":{"op":0},
    "ramp":{"op":0},
    "set_pwm":{"op":0},
    "wait":{"op":0},
    "branch":{"op":0},
    "end":{"op":0},
}


def parse(src):
    pc_instruction = 0x0
    labels = {}
    memory = []

    for line in src:
        inst = {
            "addr": pc_instruction,
            "prg": None,
            "op": None,
            "args":[]
        }

        toks = re.split(r"\s+", line)
        inst_args = False
        for tok in toks:
            if inst_args:
                inst["args"].append(tok)
                continue

            label = re.search(r'^\w+:', tok)
            if label is not None:
                if label in labels:
                    raise ValueError("Duplicate label name")

                labels[label.group().replace(":","")] = pc_instruction

            seg = re.search(r"^\.\w+", tok)
            if seg is not None:
                inst['op'] = tok.replace(".", "")
                inst['prg'] = pc_instruction
                inst_args = True

            if tok in instruction_set:
                inst['op'] = tok
                pc_instruction += 1
                inst_args = True

        if label is None and inst['op'] is None:
            continue

        memory.append(inst)

    return memory, labels


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog='lp55xx_asm',
        description='ASM for Texas led driver LP55xx ic',
        epilog='Assemblator for led efx programm')

    parser.add_argument('src_lst')

    args = parser.parse_args()
    print(args.src_lst)

    src = open(args.src_lst)
    memory, labels = parse(src)

    asm = []
    for m in memory:
        if m['op'] == "dw":
            value = m["args"][0]
            vh = 0x0
            vl = 0x0
            if "b" in value:
                value = int(value.replace("b",""),2)
                vh = (value & 0xff00) >> 8
                vl = (value & 0x00ff)

            asm.append("0x%02x" % vh)
            asm.append("0x%02x" % vl)
        print(f"{m['addr']:02X}-> {m}")

    for l in labels:
        print(f"{l}: {labels[l]}")

    for n, a in enumerate(asm):
        if not n % 16:
            print()
        print(a, end=", ")


