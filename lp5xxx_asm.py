#!/bin/env python

import re

from instruction_set import lookup_table
from callbacks import show_msg


def parse(src):
    pc_instruction = 0x0
    labels = {}
    memory = []

    segment_addr = 0
    line_no = 1
    for line in src:
        # Skip blank line and strip
        # Remove comment string from line
        line = line.strip()
        if not line:
            continue
        line = re.sub(r";.*$", "", line)

        inst = {
            "line_no": line_no,
            "line": line,
            "addr": pc_instruction,
            "prg": None,
            "op": None,
            "args": []
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

                labels[label.group().replace(":", "")] = pc_instruction
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

        ln = len(asm_bin)
        if ln % 16:
            ln = (int(ln/16)+1)*16

        padding = [0 for i in range(ln - len(asm_bin))]

    return asm_bin + padding


def c_fmt(asm, memory, name, post="", hdr=True):
    s = ""
    c = [""]
    if hdr:
        c = ["#include <%s.h>" % name,]
    c.append("const uint8_t %s%s[]={" % (name, post))
    for i in range(32):
        s = ""
        idx = 16*i
        m = []
        if (idx+16) > len(asm):
            break
        m = asm[idx:idx+16]
        s = ",".join(list(map(lambda x: f"0x{x:02X}", m))) + ","
        c.append(s)

    c.append("};")
    d = [""]
    for m in memory:
        if m['op'] == 'segment':
            d.append(f"0x{m['prg']:02X}")

    c.append("const uint8_t %s%s_addr[]={%s};" % (name, post, ",".join(d)))

    h = [""]
    if hdr:
        h = ["#ifndef _%s_H_" % name.upper(),]
        h.append("#define _%s_H_" % name.upper())
        h.append("#include <sys.h>")
    h.append("extern const uint8_t %s[%s];" % (name, len(asm)))
    h.append("extern const uint8_t %s_addr[3];" % (name))
    if hdr:
        h.append("#endif /* _%s_H_ */" % name.upper())

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

    parser.add_argument('src', help="Engine Led programm source file")
    parser.add_argument('-o', '--out-file', dest="out_file_name", default=None,
                        help="The output file name, default is the same src-file")
    parser.add_argument('-c', '--c-fmt', action="store_true",
                        dest="c_fmt_to_file",
                        help="Generate .c and .h source file")
    parser.add_argument('-a', '--c-append', action="store_true",
                        dest="c_append_to_file",
                        help="Append generate .c and .h to exisiting files source file")

    try:
        args = parser.parse_args()
        src = open(args.src)
        memory, labels = parse(src)
        asm_bin = asm(labels, memory)
    except ValueError as e:
        print(e)
        sys.exit(1)

    src_path, src_name = os.path.split(args.src)
    name, _ = os.path.splitext(args.src)
    name = os.path.basename(name)

    if args.out_file_name is not None:
        src_path, src_name = os.path.split(args.out_file_name)
        name, _ = os.path.splitext(args.out_file_name)
        name = os.path.basename(args.out_file_name)

    filemode ='w'
    if args.c_append_to_file:
        filemode ='a'

    c_name = os.path.join(src_path, f"{name}.c")
    h_name = os.path.join(src_path, f"{name}.h")
    data = hex_fmt(asm_bin, memory)
    c, h = c_fmt(asm_bin, memory, name, hdr=not args.c_append_to_file)

    print("\nHex Output")
    print("-"*80)
    for v in data:
        print(v)
    print("-"*80, "\n")
    print("\nC output")
    print("-"*80)
    for v in c:
        print(v)
    for v in h:
        print(v)
    print("-"*80, "\n")

    hex_name = os.path.join(src_path, f"{name}.hex")
    with open(hex_name, 'w') as f:
        f.write("\n".join(data))

    if args.out_file_name or args.c_append_to_file:
        with open(c_name, filemode) as f:
            f.write("\n".join(c))
        with open(h_name, filemode) as f:
            f.write("\n".join(h))

