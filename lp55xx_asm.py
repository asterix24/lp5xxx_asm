#!/bin/env python

import re

from instruction_set import lookup_table
from callbacks import show_msg


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
        is_label = False
        is_segment = False
        for tok in toks:
            if inst_args and tok:
                inst["args"] += tok.split(",")
                inst["args"] = list(filter(len, inst["args"]))
                continue

            label = re.search(r'^\w+:', tok)
            if label is not None:
                if label in labels:
                    raise ValueError(show_msg("Error", inst, "Wrong label"))

                labels[label.group().replace(":","")] = pc_instruction
                is_label = True

            seg = re.search(r"^\.\w+", tok)
            if seg is not None:
                inst['op'] = tok.replace(".", "")
                inst['prg'] = pc_instruction
                segment_addr = pc_instruction
                inst_args = True
                is_segment = True

            if tok in lookup_table:
                inst['op'] = tok
                inst['prg'] = segment_addr
                pc_instruction += 1
                inst_args = True
            else:
                if tok and not (is_label or is_segment):
                    raise ValueError(show_msg("Error", inst, "No valid opcode"))

        if label is None and inst['op'] is None:
            continue

        memory.append(inst)

    return memory, labels

def asm(labels, memory):
    asm_bin = []
    for m in memory:
        print(f"{m['addr']:02X}-> {list(m.values())}")

        if m['op'] is None:
            continue

        if not m['op'] in lookup_table:
            raise ValueError(show_msg("Error", m, "unknow instruction"))

        complie_op = lookup_table[m['op']]['callback']
        asm_bin += complie_op(m['op'], lookup_table, labels, m)

        l = len(asm_bin)
        if l % 16:
            l = (int(l/16)+1)*16

        padding = [0 for i in range(l - len(asm_bin))]

    return asm_bin + padding


def hex_fmt(asm, memory, filename=None):
    asm = asm + [ 0 for i in range((32*16) - len(asm))]

    f = None
    if filename is not None:
        out_filename = f"{name}.hex"
        f = open(out_filename, 'w')

    for n, i in enumerate(asm):
        if not n % 16:
            print()
            if filename is not None:
                f.write(f"\n")
        s = f"{i:02X} "
        print(s, end="")
        if filename is not None:
            f.write(s)

    print()
    if filename is not None:
        f.write(f"\n")

    for m in memory:
        if m['op'] == 'segment':
            s = f"@ {m['prg']:02X} {m['args'][0]}"
            print(s)
            if filename is not None:
                f.write(f"{s}\n")

    if filename is not None:
        f.close()

def c_fmt(asm, memory, name):
    f = open("%s.c" % name, 'w')
    h = open("%s.h" % name, 'w')

    name = os.path.basename(name)
    f.write("const uint8_t %s = {" % name)
    for n, i in enumerate(asm):
        if not n % 16:
            f.write(f"\n")
        f.write(f"0x{i:02X}, ")

    f.write(f"\n")
    f.write("};\n")

    f.write("const uint8_t %s_addr = {" % name)
    for m in memory:
        if m['op'] == 'segment':
            f.write(f"0x{m['prg']:02X}, ")
    f.write("};")

    f.close()

if __name__ == "__main__":
    import argparse
    import sys
    import os

    parser = argparse.ArgumentParser(
        prog='lp55xx_asm',
        description='ASM for Texas led driver LP55xx ic',
        epilog='Assemblator for led efx programm')

    parser.add_argument('src_lst')
    parser.add_argument('-o', '--hex-fmt', action="store_true", dest="hex_fmt_to_file")
    parser.add_argument('-c', '--c-fmt', action="store_true", dest="c_fmt_to_file")

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

    out_filename = None
    name = os.path.splitext(args.src_lst)[0]

    if args.hex_fmt_to_file:
        hex_fmt(asm_bin, memory, name)

    if args.c_fmt_to_file:
        c_fmt(asm_bin, memory, name)

