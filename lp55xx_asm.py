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



memory = []
pc_instruction = 0x0

label_rgex = r'^\w+:'

def parse(line):
    global pc_instruction

    inst = [
        pc_instruction,
        None,
        {
            "label":None,
            "args":[]
        }
    ]

    toks = re.split(r"\s+", line)
    inst_args = False
    for tok in toks:
        if inst_args:
            inst[2]["args"].append(tok)
            continue

        label = re.search(label_rgex, tok)
        if label is not None:
            inst[2]["label"] = label.group().replace(":","")

        seg = re.search(r"^\.\w+", tok)
        if seg is not None:
            inst[1] = tok.replace(".", "")
            pc_instruction += 1
            inst_args = True

        if tok in instruction_set:
            inst[1] = tok
            pc_instruction += 1
            inst_args = True


    if inst[2]['label'] is None and inst[1] is None:
        return

    memory.append(inst)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog='lp55xx_asm',
        description='ASM for Texas led driver LP55xx ic',
        epilog='Assemblator for led efx programm')

    parser.add_argument('src_lst')

    args = parser.parse_args()
    print(args.src_lst)


    with open(args.src_lst) as f:
        for line in f:
            parse(line.strip())


    asm = []
    for m in memory:
        if m[1] == "dw":
            value = m[2]["args"][0]
            vh = 0x0
            vl = 0x0
            if "b" in value:
                value = int(value.replace("b",""),2)
                print(value)
                vh = (value & 0xff00) >> 8
                vl = (value & 0x00ff)

            asm.append("0x%02x" % vh)
            asm.append("0x%02x" % vl)
        print(f"{m}")

    for n, a in enumerate(asm):
        if not n % 16:
            print()
        print(a, end=", ")


