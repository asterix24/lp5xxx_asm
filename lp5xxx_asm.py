#!/bin/env python

import re
import logging

from instruction_set import lookup_table
from callbacks import show_msg


def parse(src, log):
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


def asm(labels, memory, log):
    asm_bin = []
    for m in memory:
        log.debug(f"{m['addr']:02X}-> {list(m.values())}")

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

def deasm(bin, addr, log):
    if len(addr) < 3:
        raise ValueError(show_msg("Error", m, "wrong address table"))

    memory = []
    for i in range(len(bin)//2):
        b = bin[i*2] << 8 | bin[i*2+1]
        memory.append(b)

    vars = memory[:addr[0]]
    #m = bin[addr[0]:]
    #eng1 = bin[addr[0]:addr[1]]
    #eng2 = bin[addr[1]:addr[2]]
    #eng3 = bin[addr[2]:]
    print(vars)
    print(addr)
    #for i in memory[addr[0]:]:
    #    print(f"{i:04x}")

    idx = 1
    for n, i in enumerate(memory):
        op_name = []
        op_st = ""
        if n < addr[0]:
            op_st = f"a{n}: dw {i:016b}b"
            continue
        for op in lookup_table:
            for k in [('op', 'mask'), ('opv', 'maskv')]:
                opk, mk = k
                if opk not in lookup_table[op]:
                    continue
                p = lookup_table[op][opk]
                if p is None:
                    continue

                v = i & ~lookup_table[op][mk]
                if v == p:
                    op_st = f"{v:04x} {p:04x}"
                    op_name.append(op)

        if n in addr:
            print(f".segment program{idx}")
            idx += 1
        print(f"{n:03d}: {i:04x} {op_st} {op_name}")



def __bin_to_table(bin):
    c = []
    for i in range(32):
        s = ""
        idx = 16*i
        m = []
        if (idx+16) > len(bin):
            break
        m = bin[idx:idx+16]
        s = ",".join(list(map(lambda x: f"0x{x:02X}", m))) + ","
        c.append(s)

    return "\n".join(c)

def __memory_ddr_to_table(memory):
    d = []
    for m in memory:
        if m['op'] == 'segment':
            d.append(f"0x{m['prg']:02X}")
    return ", ".join(d)


HEADER_DATA = """
extern const uint8_t <NAME><POST>[<BIN_LEN>];
"""
HEADER_DATA_ADDR = """
extern const uint8_t <NAME><POST>_addr[3];
"""

HEADER_TEMPLAE=f"""
#ifndef _<NAME>_H_
#define _<NAME>_H_
#include <sys.h>

<SRC>

#endif /* _<NAME>_H_ */

"""

SOURCE_DATA="""
const uint8_t <NAME><POST>[]={
<DATA>
};

"""

SOURCE_DATA_ADDR="""
const uint8_t <NAME><POST>_addr[]={<DATA>};
"""

SOURCE_TEMPLAE="""
#include <<NAME>.h>

<SRC>

"""

def c_fmt_merge(asm_data, c_name=None, h_name=None, hdr=True, post=""):

    if c_name is None and h_name is None:
        for x in asm_data:
            c_name = os.path.join(x['path'], x['name']+".c")
            h_name = os.path.join(x['path'], x['name']+".h")
            name = x['name']

            with open(c_name, 'w') as f:
                src = SOURCE_TEMPLAE
                src = src.replace("<NAME>", name.lower())
                src = src.replace("<POST>", post)

                d = SOURCE_DATA.replace("<NAME>", name.lower())
                d = d.replace("<POST>", post)
                d = d.replace("<DATA>", __bin_to_table(x['bin']))

                d += SOURCE_DATA_ADDR.replace("<NAME>", name.lower())
                d = d.replace("<POST>", post)
                d = d.replace("<DATA>", __memory_ddr_to_table(x['memory']))

                src = src.replace("<SRC>", d)

                f.write(src)

            with open(h_name, 'w') as f:
                src = HEADER_TEMPLAE
                src = src.replace("<NAME>", name.lower())
                src = src.replace("<POST>", post)

                d = HEADER_DATA.replace("<NAME>", name.lower())
                d = d.replace("<BIN_LEN>", f"{len(x['bin'])}")
                d += HEADER_DATA_ADDR.replace("<NAME>", name.lower())
                d = d.replace("<POST>", post)

                src = src.replace("<SRC>", d)

                f.write(src)
    else:
        src = SOURCE_TEMPLAE
        c, _ = os.path.splitext(c_name)
        c = os.path.basename(c)
        src = src.replace("<NAME>", c)
        with open(c_name, 'w') as f:
            d = ""
            for x in asm_data:
                name = x['name']
                d += SOURCE_DATA.replace("<NAME>", name.lower())
                d = d.replace("<POST>", post)
                d = d.replace("<DATA>", __bin_to_table(x['bin']))

                d += SOURCE_DATA_ADDR.replace("<NAME>", name.lower())
                d = d.replace("<POST>", post)
                d = d.replace("<DATA>", __memory_ddr_to_table(x['memory']))

            src = src.replace("<SRC>", d)
            f.write(src)

        src = HEADER_TEMPLAE
        h, _ = os.path.splitext(h_name)
        h = os.path.basename(h)
        src = src.replace("<NAME>", h)
        with open(h_name, 'w') as f:
            d = ""
            for x in asm_data:
                d += HEADER_DATA.replace("<NAME>", name.lower())
                d = d.replace("<BIN_LEN>", f"{len(x['bin'])}")
                d += HEADER_DATA_ADDR.replace("<NAME>", name.lower())
                d = d.replace("<POST>", post)

            src = src.replace("<SRC>", d)
            f.write(src)


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

    parser.add_argument('files_src', nargs='+',
                        help='Engine Led assembly source file')

    parser.add_argument('-v', '--verbose', dest="verbose", action="store_true",
                        default=False, help="Verbose")

    parser.add_argument('-o', '--out-c-source-file', nargs=2, metavar=('c_filename', 'h_filename'), default=None,
                        help='If you want to use different file name for default source file. \
                        With multiple asm source, this option append all out bin in two .c .h source file')

    parser.add_argument('-c', '--c-fmt', action="store_true",
                        dest="c_fmt_to_file",
                        help="Generate .c and .h source file")

    args = parser.parse_args()

    level = logging.WARNING
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level, format='%(asctime)s [%(levelname)s]: %(message)s')

    try:
        asm_data = []
        for f in args.files_src:
            src = open(f)
            logging.debug(f)
            memory, labels = parse(src, logging)
            asm_bin = asm(labels, memory, logging)

            src_path, src_name = os.path.split(f)
            name, _ = os.path.splitext(f)
            name = os.path.basename(name)

            asm_data.append({
                'path': src_path,
                'name': name,
                'memory': memory,
                'labels': labels,
                'bin' : asm_bin
            })
    except ValueError as e:
        logging.error(f"{e}")
        sys.exit(1)


    for x in asm_data:
        data = hex_fmt(x['bin'], x['memory'])
        fn = os.path.join(x['path'], f"{x['name']}"+".hex")
        with open(fn, 'w') as f:
            f.write("\n".join(data))

    if args.c_fmt_to_file:
        c_name = None
        h_name = None
        logging.info(f"{args.out_c_source_file}")
        if args.out_c_source_file is not None:
            for i in args.out_c_source_file:
                if '.h' in i:
                    h_name = i
                if '.c' in i:
                    c_name = i

        logging.debug(f"{c_name}, {h_name}")
        c_fmt_merge(asm_data, c_name, h_name)
