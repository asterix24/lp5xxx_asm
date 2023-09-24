#!/bin/env python

import re

from instruction_set import lookup_table


def parse(src):
    pc_instruction = 0x0
    labels = {}
    memory = []

    segment_addr = 0
    line_no = 0
    for line in src:
        # Skip blank line and strip
        # Remove comment string from line
        line = line.strip()
        if not line:
            continue
        line = re.sub(r";.*$", "", line)

        inst = {
            "line_no":line_no,
            "line": line,
            "addr": pc_instruction,
            "prg": None,
            "op": None,
            "args":[]
        }

        line_no += 1
        toks = re.split(r"\s+", line)
        inst_args = False
        for tok in toks:
            if inst_args and tok:
                inst["args"] += tok.split(",")
                inst["args"] = list(filter(len, inst["args"]))
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
                segment_addr = pc_instruction
                inst_args = True

            if tok in lookup_table:
                inst['op'] = tok
                inst['prg'] = segment_addr
                pc_instruction += 1
                inst_args = True

        if label is None and inst['op'] is None:
            continue

        memory.append(inst)

    return memory, labels

def asm(labels, memory):
    asm_bin = []
    for m in memory:
        print(f"{m['addr']:02X}-> {m}")
        if m['op'] is None:
            continue

        if not m['op'] in lookup_table:
            raise ValueError(f"unknow instruction set {m['op']}")

        complie_op = lookup_table[m['op']]['callback']
        asm_bin += complie_op(m['op'], lookup_table, labels, m)

        l = len(asm_bin)
        if l % 16:
            l = (int(l/16)+1)*16

        padding = ["0x00" for i in range(l - len(asm_bin))]

    return asm_bin + padding

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog='lp55xx_asm',
        description='ASM for Texas led driver LP55xx ic',
        epilog='Assemblator for led efx programm')

    parser.add_argument('src_lst')

    try:
        args = parser.parse_args()
        print(args.src_lst)

        src = open(args.src_lst)
        memory, labels = parse(src)

        for l in labels:
            print(f"{l}: {labels[l]:02X}")

        asm_bin = asm(labels, memory)
    except ValueError as e:
        print(e)
        sys.exit(1)


    for n, a in enumerate(asm_bin):
        if not n % 16:
            print()
        print(a, end=", ")


