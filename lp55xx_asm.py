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

def c_fmt(asm, memory, name):
    s = ""
    c = ["const uint8_t %s[]={" % name,]
    for i in range(32):
        s = ""
        idx = 16*i
        m = []
        if (idx+16) > len(asm):
            break
        m = asm[idx:idx+16]
        s = ",".join(list(map(lambda x: f"0x{x:02X}", m)))
        c.append(s)

    c.append("};")
    d = []
    for m in memory:
        if m['op'] == 'segment':
            d.append(f"0x{m['prg']:02X}")

    c.append("const uint8_t %s_addr[]={%s};" % (name,",".join(d)))

    h = ["#ifndef",]
    h.append("#define _%s_H" % name.upper())
    h.append("extern const uint8_t %s[%s];" % (name, len(asm)))
    h.append("extern const uint8_t %s_addr[3];" % (name))
    h.append("/* _%s_H */" % name.upper())

    return c, h

def hex_fmt(asm, memory):
    out = []
    s = ""
    for i in range(32):
        s = ""
        idx = 16*i
        m = [0 for x in range(16)]
        if (idx+16) <= len(asm):
            m = asm[idx:idx+16]
        s = " ".join(list(map(lambda x: f"{x:02X}", m)))
        out.append(s)

    for m in memory:
        if m['op'] == 'segment':
            s = f"@ {m['prg']:02X} {m['args'][0]}"
            out.append(s)
    return out

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

    path_file_name = os.path.splitext(args.src_lst)[0]
    name = os.path.basename(path_file_name)

    data = hex_fmt(asm_bin, memory)
    for v in data:
        print(v)

    c, h = c_fmt(asm_bin, memory, name)
    for v in c:
        print(v)
    for v in h:
        print(v)

    if args.hex_fmt_to_file:
        f = open(f"{path_file_name}.hex", 'w')
        for v in data:
            f.write(v+"\n")
        f.close()

    if args.c_fmt_to_file:
        f = open(f"{path_file_name}.c", 'w')
        for v in c:
            f.write(v+"\n")
        f.close()
        f = open(f"{path_file_name}.h", 'w')
        for v in h:
            f.write(v+"\n")
        f.close()

